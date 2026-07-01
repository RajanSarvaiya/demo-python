# User Registration & Job Profile API

A backend REST API built with **FastAPI** that lets users register with
job-profile data, log in with **JWT** authentication, and retrieve their own
profile. Passwords are hashed with **bcrypt**; data is persisted via
**SQLAlchemy** with **Alembic** migrations.

The spec targets **PostgreSQL**, but the code is **database-agnostic**: it runs
on SQLite out of the box for local development and switches to PostgreSQL by
changing a single environment variable — no code changes.

---

## Project structure

```
fastapi_user_app/
├── app/
│   ├── main.py              # FastAPI app: CORS, routers, startup
│   ├── config.py            # Settings from environment (.env)
│   ├── database.py          # Engine / session / Base + get_db dependency
│   ├── dependencies.py      # get_current_user (OAuth2PasswordBearer)
│   ├── models/
│   │   └── user.py          # SQLAlchemy User model
│   ├── schemas/
│   │   └── user.py          # Pydantic: UserCreate, UserResponse, Token
│   ├── routers/
│   │   ├── auth.py          # POST /api/register, POST /api/login
│   │   └── users.py         # GET  /api/users/me
│   ├── services/
│   │   └── auth_service.py  # User CRUD + JWT create/decode
│   └── utils/
│       └── security.py      # bcrypt hash / verify
├── alembic/                 # Migration environment + versions/
├── alembic.ini
├── .env / .env.example
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Install dependencies

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and adjust values:

```env
# Local dev (default — no database server required):
DATABASE_URL=sqlite:///./app.db
# Production target:
# DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/jobdb

JWT_SECRET_KEY=change-this-to-a-long-random-secret-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> **Security:** always set a strong, unique `JWT_SECRET_KEY` outside of dev.

### 3. Create the database schema

Using Alembic (recommended):

```bash
alembic upgrade head
```

> The app also calls `Base.metadata.create_all()` on startup for convenience, so
> it works even without running migrations. For production, rely on Alembic and
> remove/guard that call.

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

Open the interactive docs at **http://127.0.0.1:8000/docs**.

---

## Using PostgreSQL instead of SQLite

1. Install the driver: `pip install psycopg2-binary` (already in
   `requirements.txt`).
2. Create a database, e.g. `jobdb`.
3. Set `DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/jobdb`
   in `.env`.
4. Run `alembic upgrade head`.

On PostgreSQL the `id` column becomes a native `UUID`, `skills` becomes a native
`TEXT[]` array, and timestamps use `TIMESTAMPTZ` — all transparently, from the
same models.

---

## API reference

Base URL: `http://127.0.0.1:8000`

### `POST /api/register` → **201 Created**

Request:
```json
{
  "name": "Rahul Sharma",
  "email": "rahul@example.com",
  "phone_number": "+919876543210",
  "password": "SecurePass123",
  "job_title": "Backend Developer",
  "skills": ["Python", "FastAPI", "PostgreSQL"],
  "job_description": "Building scalable REST APIs and microservices."
}
```

Response:
```json
{
  "id": "0c897aef-2eca-4182-b804-f28eee114675",
  "name": "Rahul Sharma",
  "email": "rahul@example.com",
  "phone_number": "+919876543210",
  "job_title": "Backend Developer",
  "skills": ["Python", "FastAPI", "PostgreSQL"],
  "job_description": "Building scalable REST APIs and microservices.",
  "created_at": "2026-07-01T10:00:00Z"
}
```

**Validation:** valid & unique email; unique phone (7–15 digits, optional `+`);
password ≥ 8 chars; `skills` non-empty; all fields required except
`job_description`.

**Errors:** `409` (email/phone already exists), `422` (validation error).

### `POST /api/login` → **200 OK**

Request:
```json
{ "email": "rahul@example.com", "password": "SecurePass123" }
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Errors:** `401` (invalid credentials).

### `GET /api/users/me` → **200 OK**

Header: `Authorization: Bearer <access_token>`

Returns the same profile shape as `register`. **Errors:** `401`
(missing/invalid/expired token).

---

## Testing via Swagger UI (`/docs`)

1. **Register** — expand `POST /api/register`, fill in the job data, execute →
   expect **201**.
2. **Login** — expand `POST /api/login`, submit email + password → copy the
   `access_token` from the response.
3. **Authorize** — click the **Authorize** button (top-right) and paste the
   token to send it as `Authorization: Bearer <token>` on subsequent requests.
4. **Get profile** — execute `GET /api/users/me` → confirm it returns the exact
   data you registered.

---

## Security notes

- Passwords are hashed with **bcrypt** and never stored or returned in plain
  text — `password_hash` appears in **no** API response.
- JWTs are signed with `JWT_SECRET_KEY` and expire after
  `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60).
- `/api/users/me` is protected by the `OAuth2PasswordBearer` scheme.
- CORS is open (`*`) by default for easy frontend integration — restrict
  `allow_origins` in `app/main.py` for production.
