from fastapi import FastAPI

from routers import rate_router
from services.db_service import Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(rate_router)
