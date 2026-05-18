# SkyQuery Localhost Development Guide

This guide provides instructions for running and developing SkyQuery fully in **localhost mode**.

## System Prerequisites
Ensure you have the following running on your machine:
- **Docker Compose** (for Trino, Postgres, and Redis)
- **Python 3.10+** (for FastAPI backend)
- **Node.js 18+** (for Next.js frontend)

---

## 1. Infrastructure Setup (Docker)

To spin up the databases (Trino, Postgres) and session store (Redis) locally:

```bash
cd infrastructure
docker compose up -d
```

Verify that all services are healthy and running on their respective ports:
- **Trino Coordinate**: `http://localhost:8080`
- **Postgres Database**: `localhost:5432`
- **Redis Cache**: `localhost:6379`

---

## 2. Backend Startup

1. Open a terminal in the `backend` directory.
2. Ensure your local `.env` contains:
   ```env
   TRINO_HOST=localhost
   TRINO_PORT=8080
   TRINO_USER=admin
   TRINO_CATALOG=aviation
   TRINO_SCHEMA=public
   MOCK_EXECUTION=false
   FRONTEND_URL=http://localhost:3000
   ```
3. Run the backend dev server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend API will be available at `http://localhost:8000`.

---

## 3. Frontend Startup

1. Open a terminal in your Next.js frontend directory (`c:\Users\shrey\Downloads\title-gradient-refinement (1)`).
2. Ensure your `.env.local` contains:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```
   The frontend UI will be available at `http://localhost:3000`.

---

## 4. Key Localhost Features & Flows

- **GitHub Copilot Auth Flow**: When continuing with GitHub, the backend handles OAuth session exchanges and persists user sessions inside the local Redis cache. Starlette Session middleware is set to `lax` and `https_only=False` to ensure smooth local cookie exchanges over HTTP.
- **REST API Port**: The frontend interacts directly with `http://localhost:8000` via headers and REST queries.
- **Robust Session Restoration**: In case browsers block cookie exchanges on localhost, the frontend will automatically attach authorization headers (`Authorization` and `X-Session-ID`) to every fetch call, ensuring seamless session validation.
