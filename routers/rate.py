from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from requests import request
from sqlalchemy.orm import Session

from models import Rate
from services.db_service import get_db

router = APIRouter(prefix="/rates", tags=["Rate"])

NBP_API_URL = "https://api.nbp.pl/api/exchangerates/tables"


@router.get("/")
async def get_all_rates(db: Annotated[Session, Depends(get_db)]):
    return db.query(Rate).all()


@router.get("/{date}")
async def get_rates_for_requested_date(
        db: Annotated[Session, Depends(get_db)],
        request_date: str = Query(..., description="Date in YYYY-MM-DD format")):
    return db.query(Rate).filter(Rate.update_date == request_date).all()


@router.post("/fetch")
async def download_rates(
        db: Annotated[Session, Depends(get_db)],
        table: str = Query(default="A"),
        date_from: date = Query(default=date.today()),
        date_to: date = Query(default=date.today()),
):
    response = request("get", f"{NBP_API_URL}/{table}/{date_from}/{date_to}").json()
    return response
