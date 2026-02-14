import os
from fastapi import APIRouter, HTTPException
from services.db_service import Base, engine
router = APIRouter(prefix="/test", tags=["Test"])


@router.post("/reset-db")
def reset_database():
    if os.getenv("ENVIRONMENT") != "TEST":
        raise HTTPException(
            status_code=403,
            detail="Forbidden: This endpoint is only available in the test environment."
        )

    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        return {"status": "success", "message": "Database reset successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database reset failed: {str(e)}")