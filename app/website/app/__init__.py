from flask import Flask
from app.db import db
from app.models import User

from werkzeug.security import generate_password_hash

import os
import secrets


app = Flask(__name__)

db_user = os.getenv('DB_USER', 'router_app')
db_password = os.getenv('DB_PASSWORD', 'router_app_change_me')
db_host = os.getenv('DB_HOST', 'db')
db_name = os.getenv('DB_NAME', 'database')

app.secret_key = os.getenv('APP_SECRET_KEY', secrets.token_urlsafe(64))

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

# Session hardening
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', '0') == '1'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800

# Create database tables
db.init_app(app)
app.app_context().push()
db.create_all()


def _seed_users() -> None:
    default_user_password = os.getenv('TEST_USER_PASSWORD', 'test123!ChangeMe')
    admin_password = os.getenv('ADMIN_PASSWORD')
    if not admin_password:
        admin_password = secrets.token_urlsafe(24)

    test = User.query.filter_by(username='test').first()
    if not test:
        test = User(
            username='test',
            password=generate_password_hash(default_user_password),
            name='John',
            lastname='Doe',
            email='john@example.com',
            is_admin=False,
        )
        db.session.add(test)

    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=generate_password_hash(admin_password),
            name='Administrator',
            lastname='System',
            email='admin@example.com',
            is_admin=True,
        )
        db.session.add(admin)

    db.session.commit()


_seed_users()

# Include routes
from app import routes