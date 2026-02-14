import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import rate_router, test_router
from services.db_service import Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(rate_router)
if os.getenv("ENVIRONMENT") == "TEST":
    app.include_router(test_router)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://test-app-frontend:3000" # For cypress tests
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
