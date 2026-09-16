# Set Together

A shared workout leaderboard for gym friend groups. Create a group, share the
invite code, log your sessions, and see who's actually showing up.

Built to practice the parts of shipping software that don't show up in a
classroom project: real authentication, authorization (not just login),
containerization, and a CI pipeline that runs on every push.

## Architecture

```
frontend (React + Vite)  --JWT-->  backend (FastAPI)  -->  Postgres (Supabase)
        |                                                        ^
        +---------------------- Supabase Auth (signup/login) ----+
```

- **Auth**: Supabase Auth handles signup, login, and issuing a signed JWT.
  The backend never sees a password - it only verifies the JWT's signature
  and reads the user ID out of it (`backend/app/auth.py`).
- **Authorization**: separate from authentication. Being logged in gets you
  a valid token; being a *member of a group* is checked before you can log
  or view its workouts (`require_membership` in `groups.py`); owning a
  specific workout log is checked before you can delete it
  (`workouts.py::delete_workout`). These are two different, deliberately
  separate checks.
- **Data model**: `groups` -> `group_members` (join table) -> `workout_logs`,
  every log foreign-keyed to a real user ID. See `backend/app/models.py`.
- **Tests**: run against an in-memory SQLite DB with auth mocked via FastAPI's
  dependency override system, so the suite runs in CI without any live
  database or real credentials (`backend/tests/`).

## Running it locally

### 1. Create a Supabase project (free, ~2 minutes)

1. Go to [supabase.com](https://supabase.com), create a project.
2. **Project Settings -> API**: copy the Project URL, anon/public key, and
   JWT Secret.
3. **Project Settings -> Database -> Connection string (URI)**: copy the
   connection string (use the "Transaction" pooler for the port).

### 2. Backend

```bash
cd backend
cp .env.example .env       # fill in DATABASE_URL and SUPABASE_JWT_SECRET
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# create tables
python -c "from app.database import Base, engine; from app import models; Base.metadata.create_all(engine)"

uvicorn app.main:app --reload
```

Runs at `http://localhost:8000`. Check `/health`.

### 3. Frontend

```bash
cd frontend
cp .env.example .env.local  # fill in VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY
npm install
npm run dev
```

Runs at `http://localhost:5173`.

### 4. Or run both with Docker

```bash
# from repo root, with backend/.env filled in and these exported:
export VITE_SUPABASE_URL=...
export VITE_SUPABASE_ANON_KEY=...

docker compose up --build
```

## Running tests

```bash
cd backend
pytest -v
```

No live database needed - the suite spins up an in-memory SQLite DB per test
and fakes an authenticated user via dependency injection.

## CI/CD

`.github/workflows/ci.yml` runs the backend test suite on every push, and
on merge to `main`, builds both Docker images to confirm they build cleanly
(image pushing/deploying is left as a next step - see below).

## Deploying (next steps)

- **Frontend**: build with `npm run build`, push `frontend/dist` to an S3
  bucket configured for static hosting, served through CloudFront.
- **Backend**: push the Docker image to ECR, run it on a small Fargate
  service or a single EC2 instance behind an ALB. Point `DATABASE_URL` at
  the same Supabase Postgres instance.
- Add the image-push and deploy steps to the `build-images` job in
  `ci.yml`, gated on `secrets.AWS_*` credentials stored in the repo.

## What I'd build next

- Weekly leaderboard reset / all-time vs. this-week toggle
- Push notifications when a friend logs a session
- Rate limiting on workout logging to prevent spam
