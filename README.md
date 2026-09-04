# TaskFlow API

A small, production-shaped REST API demonstrating clean backend architecture: JWT authentication, ownership-scoped resources, filtering, and a full automated test suite.

Built to show working patterns for a client-facing API — auth, validation, error handling, and tests — the same structure used for real client work, just with a generic domain (tasks) instead of client-specific business logic.

## Features

- **JWT authentication** — register and log in, receive a bearer token
- **Ownership-scoped resources** — users can only see and modify their own tasks (returns 403 on cross-user access attempts, covered by a test)
- **Full CRUD** — create, list, retrieve, update, and delete tasks
- **Filtering** — list tasks by completion status and priority via query params
- **Interactive API docs** — auto-generated at `/docs` (Swagger UI) and `/redoc`
- **Automated test suite** — 10 tests covering auth flows, CRUD, filtering, and access control, run with `pytest`

## Tech stack

Python · FastAPI · SQLAlchemy · Pydantic · JWT (python-jose) · bcrypt password hashing · pytest

## Running locally

```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API explorer — you can register a user, log in, and try every endpoint directly from the browser.

## Running the tests

```bash
pytest tests/ -v
```

## Example usage

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'

# Log in (returns a JWT)
curl -X POST http://localhost:8000/auth/login \
  -d "username=you@example.com&password=yourpassword"

# Create a task (replace TOKEN with the access_token from login)
curl -X POST http://localhost:8000/tasks/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Ship the API", "priority": "high"}'
```

## Project structure

```
app/
  main.py           # App entrypoint, router registration
  database.py        # SQLAlchemy engine/session setup
  models.py          # ORM models (User, Task)
  schemas.py          # Pydantic request/response schemas
  auth.py            # Password hashing, JWT creation/validation
  routers/
    auth_routes.py    # /auth/register, /auth/login
    tasks.py          # /tasks CRUD + filtering
tests/
  test_api.py         # Full test suite (auth, CRUD, access control)
```

## Notes

This is a portfolio/demo project showing backend patterns, not a live production service — the SQLite database and dev secret key are intentionally simple for local running. For a real client project, this same structure adapts directly: swap SQLite for Postgres, move the secret key to environment variables/a secrets manager, and add the client's actual domain logic in place of tasks.

---

Built by [Your Name] — available for backend and API development work. [Link to Fiverr/Upwork profile]
