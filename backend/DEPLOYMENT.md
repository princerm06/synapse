# Backend deployment

Milestone 5A packages the Synapse FastAPI backend as a Docker container and
moves deployment-sensitive settings into environment variables.

## Local container smoke test

From the repository root:

```bash
docker build -t synapse-backend ./backend
docker run --rm -p 8000:8000 \
  --env-file backend/.env \
  -e APP_ENV=development \
  synapse-backend
```

Then verify:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","environment":"development"}
```

## Production configuration

A deployed environment must provide:

- `DATABASE_URL`
- `APP_ENV=production`
- `CORS_ORIGINS` with an explicit comma-separated allowlist
- optionally `PORT` if the hosting platform injects a non-default port

Production mode intentionally refuses to start with wildcard CORS.

## Current boundary

This milestone makes the backend portable and deployment-ready. It does not yet:

- deploy the image to a cloud host
- replace localhost URLs in the extension/frontend
- add authentication or per-user isolation
- add an asynchronous ingestion worker

Those belong to the following cloud milestones.
