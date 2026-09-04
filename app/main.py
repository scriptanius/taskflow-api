from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth_routes, tasks

Base.metadata.create_all(bind=engine)

DESCRIPTION = """
A demo REST API showing authenticated CRUD, ownership-scoped resources, filtering,
and a full automated test suite — built with FastAPI, SQLAlchemy, and JWT auth.

**Also demonstrates proper error handling** — try registering the same email
twice (400), accessing `/tasks` without logging in (401), or fetching a task
that belongs to another user (403) to see clear, correctly-coded error
responses rather than raw crashes or unhelpful 500s.

## 👀 How to try this API right now (takes ~1 minute)

This page is a live, interactive API explorer — you can call every endpoint
below directly from your browser, no separate tools needed.

1. **Register a user** — open `POST /auth/register` below, click **Try it out**,
   enter any email/password, and click **Execute**.
2. **Click the green "Authorize" button** at the top right of this page.
   A form will appear asking for `username`, `password`, `client_id`, and
   `client_secret`.
   - **username**: the email you just registered with
   - **password**: the password you just registered with
   - **client_id** and **client_secret**: leave both blank
   - Click **Authorize**, then **Close**.
3. **You're authenticated.** Behind the scenes, this page just logged you in
   and attached the resulting token to every request automatically. Every
   endpoint under `tasks` will now work when you click **Try it out** →
   **Execute** — create a task, list your tasks, mark one complete, or delete it.

That's the same login flow a real client app would perform on your behalf —
this page just makes it visible so you can test it manually.

Full source code, architecture notes, and a local setup guide are in the
[GitHub repository](https://github.com/scriptanius/taskflow-api).
"""

app = FastAPI(
    title="TaskFlow API",
    description=DESCRIPTION,
    version="1.0.0",
    openapi_tags=[
        {
            "name": "auth",
            "description": "Start here — register a user, then log in to get your access token.",
        },
        {
            "name": "tasks",
            "description": (
                "Requires authentication. Click the **Authorize** button above "
                "and paste your token first, or these will return 401."
            ),
        },
        {
            "name": "health",
            "description": "Basic service status check.",
        },
    ],
)

app.include_router(auth_routes.router)
app.include_router(tasks.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "TaskFlow API"}
