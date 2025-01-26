from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Path
from requests import request
from sqlalchemy.orm import Session

from helpers import exceptions, queries, services
from helpers.exceptions import TableEnum
from models import Rate
from schemas import RateResponseSchema, RatesOnlyResponseSchema, RateCurrencyResponseSchema
from services.db_service import get_db

router = APIRouter(prefix="/currencies", tags=["Rate"])

NBP_API_URL = "https://api.nbp.pl/api/exchangerates/tables"


@router.get("/", response_model=list[RatesOnlyResponseSchema])
async def get_all_rates(db: Annotated[Session, Depends(get_db)]):
    currencies_grouped_by_date = queries.find_all_currencies_for_all_dates(db)
    if not currencies_grouped_by_date:
        exceptions.raise_404_not_found("No currencies found. Try to fetch them first.")

    return [{"update_date": update_date, "rates": currencies} for update_date, currencies in currencies_grouped_by_date]

@router.get("/currency/{currency}")
async def get_rates_for_specified_currency(
        db: Annotated[Session, Depends(get_db)],
        currency: str = Path(..., description="Currency code"),
        date_from: date = Query(default=date.today(), description="Date in YYYY-MM-DD format"),
        date_to: date = Query(default=date.today(), description="Date in YYYY-MM-DD format"),
):
    rates = queries.find_rates_for_specified_currency_and_date(db, currency, date_from, date_to)
    print(rates)
    if not rates:
        exceptions.raise_404_not_found("No rates found for requested currency. Try to download them first.")

    return [{"date": update_date, "mid": mid } for update_date, mid in rates]


@router.get("/{request_date}", response_model=list[RateResponseSchema])
async def get_rates_for_requested_date(
        db: Annotated[Session, Depends(get_db)],
        request_date: date = Path(..., description="Date in YYYY-MM-DD format")
):
    rates = queries.find_all_rates_for_specified_date(db, request_date)
    if request_date > date.today():
        exceptions.raise_400_bad_request("Date cannot be in the future.")
    if not queries.find_all_rates_for_specified_date(db, request_date):
        exceptions.raise_404_not_found("No rates found for requested date. Try to download them first.")

    return rates


@router.post("/fetch")
async def download_rates(
        db: Annotated[Session, Depends(get_db)],
        table: TableEnum = Query(..., description="Tables from NBP API", enum=["a", "b"]),
        date_from: date = Query(default=date.today(), description="Date in YYYY-MM-DD format"),
        date_to: date = Query(default=date.today(), description="Date in YYYY-MM-DD format"),
        currency: str = Query(None, description="Currency code")
):
    if date_from > date_to:
        exceptions.raise_400_bad_request("The beginning date cannot be older than the end date.")
    if date_from > date.today() or date_to > date.today():
        exceptions.raise_400_bad_request("Date cannot be in the future.")

    all_valid_rates = []

    # Split dates into periods, if request period is longer than 90 days
    split_period = 90
    if (date_to - date_from).days > split_period:
        date_periods = services.split_fetch_period(date_from, date_to, split_period)

        for date_period in date_periods:
            url = f"{NBP_API_URL}/{table.value}/{date_period[0]}/{date_period[1]}"
            data = services.fetch_rates(request("get", url))

            for record in data:
                rates_date = record.get("effectiveDate")
                rates = record.get("rates")
                valid_rates = [Rate(**rate, update_date=rates_date) for rate in rates
                               if not queries.find_rates_with_specified_code_and_date(db, rates_date, rate.get("code"))]
                all_valid_rates.extend(valid_rates)

        for rate in all_valid_rates:
            queries.add_rate_to_db(db, rate)
        return {"message": f"Added {len(all_valid_rates)} rates"}
    else:
        url = f"{NBP_API_URL}/{table.value}/{date_from}/{date_to}"
        data = services.fetch_rates(request("get", url))
        all_valid_rates = []
        for record in data:
            rates_date = record.get("effectiveDate")
            rates = record.get("rates")

            valid_rates = [Rate(**rate, update_date=rates_date) for rate in rates
                           if not queries.find_rates_with_specified_code_and_date(db, rates_date, rate.get("currency"))]
            all_valid_rates.extend(valid_rates)

    if not all_valid_rates:
        exceptions.raise_400_bad_request("All rates for specified period are already in the database.")
    for rate in all_valid_rates:
        queries.add_rate_to_db(db, rate)
    return {"message": f"Added {len(all_valid_rates)} rates"}
