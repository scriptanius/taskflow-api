import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Use an isolated in-memory SQLite DB for tests, separate from taskflow.db
TEST_DATABASE_URL = "sqlite:///./test_taskflow.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def register_and_login(email="user@example.com", password="strongpass123"):
    client.post("/auth/register", json={"email": email, "password": password})
    resp = client.post("/auth/login", data={"username": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_check():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_register_and_login():
    resp = client.post("/auth/register", json={"email": "a@example.com", "password": "pass1234"})
    assert resp.status_code == 201
    assert resp.json()["email"] == "a@example.com"

    resp = client.post("/auth/login", data={"username": "a@example.com", "password": "pass1234"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_duplicate_registration_fails():
    client.post("/auth/register", json={"email": "dup@example.com", "password": "pass1234"})
    resp = client.post("/auth/register", json={"email": "dup@example.com", "password": "pass1234"})
    assert resp.status_code == 400


def test_login_wrong_password_fails():
    client.post("/auth/register", json={"email": "b@example.com", "password": "pass1234"})
    resp = client.post("/auth/login", data={"username": "b@example.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_create_and_list_tasks():
    headers = register_and_login()
    resp = client.post("/tasks/", json={"title": "Write README", "priority": "high"}, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["title"] == "Write README"

    resp = client.get("/tasks/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_task_requires_auth():
    resp = client.get("/tasks/")
    assert resp.status_code == 401


def test_update_and_complete_task():
    headers = register_and_login()
    create_resp = client.post("/tasks/", json={"title": "Deploy API"}, headers=headers)
    task_id = create_resp.json()["id"]

    resp = client.patch(f"/tasks/{task_id}", json={"completed": True}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["completed"] is True


def test_delete_task():
    headers = register_and_login()
    create_resp = client.post("/tasks/", json={"title": "Temp task"}, headers=headers)
    task_id = create_resp.json()["id"]

    resp = client.delete(f"/tasks/{task_id}", headers=headers)
    assert resp.status_code == 204

    resp = client.get(f"/tasks/{task_id}", headers=headers)
    assert resp.status_code == 404


def test_filter_tasks_by_completed():
    headers = register_and_login()
    client.post("/tasks/", json={"title": "Task A"}, headers=headers)
    done_resp = client.post("/tasks/", json={"title": "Task B"}, headers=headers)
    client.patch(f"/tasks/{done_resp.json()['id']}", json={"completed": True}, headers=headers)

    resp = client.get("/tasks/?completed=true", headers=headers)
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Task B"


def test_user_cannot_access_others_task():
    headers_a = register_and_login(email="ownerA@example.com")
    headers_b = register_and_login(email="ownerB@example.com")

    create_resp = client.post("/tasks/", json={"title": "Private task"}, headers=headers_a)
    task_id = create_resp.json()["id"]

    resp = client.get(f"/tasks/{task_id}", headers=headers_b)
    assert resp.status_code == 403
