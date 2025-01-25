from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from requests import request
from sqlalchemy.orm import Session

from helpers import exceptions, queries
from models import Rate
from schemas import RateResponseSchema, RatesOnlyResponseSchema
from services.db_service import get_db

router = APIRouter(prefix="/currencies", tags=["Rate"])

NBP_API_URL = "https://api.nbp.pl/api/exchangerates/tables"


@router.get("/", response_model=list[RatesOnlyResponseSchema])
async def get_all_rates(db: Annotated[Session, Depends(get_db)]):
    currencies_grouped_by_date = queries.find_all_currencies_for_all_dates(db)
    if not currencies_grouped_by_date:
        exceptions.raise_404_not_found("No currencies found. Try to fetch them first.")

    return [{"update_date": update_date, "rates": currencies} for update_date, currencies in currencies_grouped_by_date]


@router.get("/{date}", response_model=list[RateResponseSchema])
async def get_rates_for_requested_date(
        db: Annotated[Session, Depends(get_db)],
        request_date: str = Query(default=date.today(), description="Date in YYYY-MM-DD format")
):
    rates = queries.find_all_rates_for_specified_date(db, request_date)
    if not db.query(Rate):
        exceptions.raise_404_not_found("No rates found for requested date. Try to download them first.")
    return rates


@router.post("/fetch")
async def download_rates(
        db: Annotated[Session, Depends(get_db)],
        table: str = Query(default="A"),
        date_from: date = Query(default=date.today()),
        date_to: date = Query(default=date.today()),
):
    response = request("get", f"{NBP_API_URL}/{table}/{date_from}/{date_to}").json()
    return response
