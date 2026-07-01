# FastAPI User App

A pure JSON REST API (no HTML frontend) for user registration and lookup.
Every endpoint accepts and returns JSON.

## Features

- **User registration** with full name, email, password, faculty, skills,
  job description, company, years of experience, and portfolio URL.
- **Validation** via Pydantic. Unique email enforced, password minimum
  6 characters, URL format checked. Errors are returned as JSON.
- **Password hashing** with bcrypt.
- **Login** endpoint that verifies credentials.
- **SQLite + SQLAlchemy ORM** so data persists between requests.

## Project structure

```
fastapi_user_app/
├── main.py            # FastAPI app + JSON routes
├── database.py        # Engine, session, Base, get_db dependency
├── models.py          # SQLAlchemy User model
├── schemas.py         # Pydantic validation schemas
├── crud.py            # DB access + password hashing helpers
├── requirements.txt
└── README.md
```

## Setup & run

1. **Create and activate a virtual environment** (recommended):

   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the development server:**

   ```bash
   uvicorn main:app --reload
   ```

4. Open **http://127.0.0.1:8000/docs** for interactive Swagger UI.

## API routes

| Method | Path                  | Description                                                       |
|--------|-----------------------|-------------------------------------------------------------------|
| GET    | `/`                   | Health/info endpoint — `{"status": "ok", "docs": "/docs"}`.       |
| POST   | `/api/register`       | Validate, hash password, save user, return created user (201).    |
| POST   | `/api/login`          | Verify email + password, return the user as JSON.                 |
| GET    | `/api/users/{user_id}`| Return a single user by id, or 404.                              |

### `POST /api/register`

Request body (`application/json`):

```json
{
  "name": "Mitul Sarvaiya",
  "email": "mitul@yopmail.com",
  "password": "secret123",
  "faculty": "developer",
  "skills": "AI, Python",
  "job_description": "Backend developer",
  "company": "Sarvaswa.AI Labs",
  "experience_years": 3,
  "portfolio_url": "https://example.com/mitul"
}
```

Responses:

- `201 Created` — JSON of the new user (password hash is never returned).
- `409 Conflict` — `{"detail": "Email already registered."}`
- `422 Unprocessable Entity` — body failed validation (e.g. password < 6 chars).

### `POST /api/login`

Request body (`application/json`):

```json
{ "email": "mitul@yopmail.com", "password": "secret123" }
```

Responses:

- `200 OK` — JSON of the user.
- `401 Unauthorized` — `{"detail": "Invalid email or password."}`

## Swagger / OpenAPI docs

FastAPI generates interactive API documentation automatically while the
server is running:

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/docs | **Swagger UI** — try each endpoint in the browser |
| http://127.0.0.1:8000/redoc | ReDoc — clean reference view |
| http://127.0.0.1:8000/openapi.json | Raw OpenAPI 3.1 schema |

## Notes

- The SQLite database file `app.db` is created automatically on first run.
