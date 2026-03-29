# RootBreach CTF - Stage 5 (Hardened Build)

This repository now contains a hardened version of the original Stage 5 setup.

## Run locally

1. Copy `.env.example` to `.env` and update secret values.
2. Start services:

```bash
docker compose up --build -d
```

3. Access the challenge web entrypoint at `http://127.0.0.1:8002`.

## Security fixes included

- Removed sensitive flag exposure (`/devices/flag/status` no longer returns secrets).
- Added token-based authorization for internal `/devices*` API calls.
- Replaced plaintext/weak session-auth logic with proper password hash verification.
- Enabled full logout invalidation (`session.clear()`).
- Removed verbose internal proxy/header leakage from user-facing responses.
- Migrated secrets and DB credentials to environment variables.
- Simplified runtime architecture by removing unnecessary proxy layers from active deployment.
- Upgraded core container baseline: MySQL `5.7` -> `8.4`.
- Tightened Apache directory options and removed wildcard CORS headers.

## Notes

- Default values in `.env.example` are placeholders for local testing.
- `docker compose` is configured to fail fast if required secrets are missing in `.env`.
- For deployment behind HTTPS, set `SESSION_COOKIE_SECURE=1`.
