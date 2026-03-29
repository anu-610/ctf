# RootBreach CTF 2026 — Stage 5 SecureShield (Hardened)

This repository contains a hardened version of the Stage 5 challenge stack.
It preserves the intended router-admin simulation while removing critical security flaws from the original implementation.

---

## Overview

The project simulates a router administration panel built with Flask and Apache, backed by MySQL.

Main goals of this hardened build:

- keep the application runnable for local/demo environments,
- remove high-risk vulnerabilities from the original code,
- enforce safer defaults for secrets, sessions, and internal service access.

---

## Architecture

Active runtime services:

- `hrs_admin_router` — Flask app served by Apache/mod_wsgi
- `db` — MySQL 8.4 backend

Port mapping:

- `http://127.0.0.1:8002` → app container port `80`

---

## Repository Structure

```text
.
├── docker-compose.yml
├── .env.example
├── app/
│   ├── Dockerfile
│   ├── hrs_admin_router-httpd.conf
│   ├── website/
│   │   └── app/
│   └── internal/
└── mysql/
	 └── Dockerfile
```

---

## Prerequisites

- Docker
- Docker Compose (v2)

---

## Quick Start

1. Create environment file from template:

```bash
cp .env.example .env
```

2. Update secret values in `.env` (recommended before any shared deployment).

3. Build and run:

```bash
docker compose up --build -d
```

4. Open in browser:

```text
http://127.0.0.1:8002
```

5. Check service health:

```bash
docker compose ps
```

---

## Default Local Login

By default, a local test account is seeded from `.env`:

- Username: `test`
- Password: value of `TEST_USER_PASSWORD` (default in `.env.example`)

Change this value for any environment beyond local testing.

---

## Security Hardening Implemented

Compared to the original challenge baseline, this build includes:

1. **Sensitive endpoint protection**
	- Removed direct flag disclosure behavior from internal status route.

2. **Internal API access control**
	- Added token-based checks for internal `/devices*` routes.

3. **Authentication fixes**
	- Replaced weak/legacy auth logic with secure hash verification.
	- Fixed pass-the-hash style logic flaw in legacy migration fallback.

4. **Session hardening**
	- Enforced clean logout invalidation using `session.clear()`.
	- Applied safer cookie defaults (`HttpOnly`, `SameSite`, optional `Secure`).

5. **Secrets and configuration hygiene**
	- Moved credentials/secrets to environment variables.
	- Added fail-fast compose requirements when required secrets are missing.

6. **Information disclosure reduction**
	- Removed verbose internal/proxy diagnostics from user-facing responses.

7. **Platform baseline improvements**
	- Upgraded MySQL image from `5.7` to `8.4`.

---

## Environment Variables

`docker-compose.yml` requires the following values (from `.env`):

- `MYSQL_ROOT_PASSWORD`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `APP_SECRET_KEY`
- `INTERNAL_API_TOKEN`

Optional:

- `SESSION_COOKIE_SECURE` (`1` for HTTPS deployments)
- `TEST_USER_PASSWORD`

If required variables are missing, compose startup intentionally fails.

---

## Useful Commands

Start services:

```bash
docker compose up -d
```

Rebuild app after code changes:

```bash
docker compose up --build -d hrs_admin_router
```

View logs:

```bash
docker compose logs -f hrs_admin_router
```

Stop services:

```bash
docker compose down
```

Reset containers + volumes (clean DB state):

```bash
docker compose down -v
```

---

## Troubleshooting

### 1) App does not open on `:8002`

- Run `docker compose ps` and confirm `hrs_admin_router` is `healthy`.
- Ensure no other process is binding port `8002`.

### 2) Database startup fails after image/version changes

- Old volumes may be incompatible after major DB upgrades.
- Run:

```bash
docker compose down -v
docker compose up -d
```

### 3) Login fails unexpectedly

- Verify `TEST_USER_PASSWORD` in `.env`.
- Rebuild app service after changing auth-related code:

```bash
docker compose up --build -d hrs_admin_router
```

---

## Notes for Submission

For Stage 5 delivery, you typically submit:

- GitHub repository link
- deployed/local running website link
- penetration testing report document

This repository is prepared to support all three with reproducible local execution.
