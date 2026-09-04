from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth_routes, tasks

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    description=(
        "A demo REST API showing authenticated CRUD, filtering, and clean structure. "
        "Built with FastAPI, SQLAlchemy, and JWT auth."
    ),
    version="1.0.0",
)

app.include_router(auth_routes.router)
app.include_router(tasks.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "TaskFlow API"}
