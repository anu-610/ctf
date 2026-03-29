from flask import render_template, redirect, url_for, request, session

from app import app
from app.db import db
from app.models import User

import os
import requests
from werkzeug.security import check_password_hash, generate_password_hash

@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


class SessionError(Exception):
    def __init__(self, message='Session verifcation failed.'):
        self.message = message
        super().__init__(self.message)


def verify_session():
    user_id = session.get('user_id')
    if not user_id:
        raise SessionError(message='Session expired. Please sign in again.')

    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise SessionError(message='Invalid username.')

    return user


def _validate_user_password(user: User, submitted_password: str) -> bool:
    stored_password = user.password or ''

    # Standard secure hash path
    if check_password_hash(stored_password, submitted_password):
        return True

    # Legacy plaintext migration fallback
    if stored_password == submitted_password:
        user.password = generate_password_hash(submitted_password)
        db.session.commit()
        return True

    return False

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return render_template('login.html', error='Username and password are required.')

        user = User.query.filter_by(username=username).first()
        if not user or not _validate_user_password(user, password):
            return render_template('login.html', error='Invalid username or password.')

        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session.permanent = True

        return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin_panel')
def admin_panel():
    try:
        user = verify_session()
    except SessionError as e:
        return render_template('login.html', error=e.message)

    if not user.is_admin:
        return render_template('dashboard.html', error_message='Only administrator users can open this section.')

    return render_template('admin_panel.html')


@app.route('/dashboard')
def dashboard():
    try:
        verify_session()
    except SessionError as e:
        return render_template('login.html', error=e.message)

    return render_template('dashboard.html')


@app.route('/wifi_settings', methods=['GET', 'POST'])
def wifi_settings():
    try:
        verify_session()
    except SessionError as e:
        return render_template('login.html', error=e.message)


    if request.method == 'GET':
        return render_template('wifi_settings.html')
    elif request.method == 'POST':
        internal_url = os.getenv('INTERNAL_STATUS_URL', 'http://127.0.0.1/devices/wifi_chipset/status')
        internal_api_token = os.getenv('INTERNAL_API_TOKEN', '')

        try:
            resp = requests.get(
                internal_url,
                headers={
                    'Host': 'internal.router',
                    'X-Internal-Auth': internal_api_token,
                },
                timeout=3,
            )
            status_hint = f'WiFi module status check returned HTTP {resp.status_code}.'
        except requests.RequestException:
            status_hint = 'WiFi module status check is temporarily unavailable.'

        return render_template(
            'wifi_settings.html',
            error_message='Settings cannot be changed right now. The WiFi chipset is still booting.',
            error_response=status_hint,
        )