from datetime import date
from typing import Annotated

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, Query, Path
from requests import request
from sqlalchemy.orm import Session

from helpers import exceptions, queries, services
from schemas import RateResponseSchema, RateResponseOnlyCurrencies
from services.db_service import get_db

NBP_API_TABLES_URL = "https://api.nbp.pl/api/exchangerates/tables/a"
NBP_API_RATES_URL = "https://api.nbp.pl/api/exchangerates/rates/a"
REQUEST_LIMIT_PERIOD = 366
TABLE_SPLIT_PERIOD = 90

router = APIRouter(prefix="/currencies", tags=["Rate"])


@router.get("/", response_model=list[RateResponseOnlyCurrencies])
async def get_all_currencies(db: Annotated[Session, Depends(get_db)]):
    currencies = queries.get_currencies(db)
    if not currencies:
        exceptions.raise_404_not_found("No currencies found. Try to fetch them first.")
    return currencies


@router.get("/{request_date}", response_model=list[RateResponseSchema])
async def get_rates(
        db: Annotated[Session, Depends(get_db)],
        request_date: str = Path(..., description="Date in YYYY, YYYY-MM, YYYY-QQ or YYYY-MM-DD format"),
        code: Annotated[str | None, Query(description="Currency code (e.g., USD, EUR)")] = None
):
    today = date.today()
    start_date = end_date = None

    try:  # Parse date parameter
        if len(request_date) == 4:  # Year only: YYYY
            year = int(request_date)
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            if end_date > today:
                end_date = today
        elif 'Q' in request_date:  # Quarter: YYYY-QQ

            year, quarter = request_date.split('-Q')
            quarter = int(quarter)
            start_date = date(int(year), 3 * quarter - 2, 1)
            end_date = start_date + relativedelta(months=3, days=-1)
            if end_date > today:
                end_date = today

        elif len(request_date.split('-')) == 2:  # Month: YYYY-MM
            year, month = map(int, request_date.split('-'))
            start_date = date(year, month, 1)
            end_date = start_date + relativedelta(months=1, days=-1)
            if end_date > today:
                end_date = today

        else:  # Full date: YYYY-MM-DD
            start_date = end_date = date.fromisoformat(request_date)

    except ValueError:
        exceptions.raise_400_bad_request(
            f"Invalid date format. "
            f"Use YYYY for year, YYYY-MM for month, YYYY-Q1/Q2/Q3/Q4 for quarter, or YYYY-MM-DD for specific date"
        )

    if start_date > today or end_date > today:
        exceptions.raise_400_bad_request("Date cannot be in the future.")

    if code is not None:
        code = code.upper()

    rates, start_date, end_date = queries.get_rates_for_period(db, start_date, end_date, code)
    if not rates and code:
        exceptions.raise_404_not_found(f"No {code} rates found for the requested period. Try to download them first.")
    elif not rates:
        exceptions.raise_404_not_found("No rates found for the requested period. Try to download them first.")

    return rates


@router.post("/fetch/tables")
async def download_rates_for_table(
        db: Annotated[Session, Depends(get_db)],
        date_from: Annotated[date | None, Query(description="Date in YYYY-MM-DD format")] = None,
        date_to: Annotated[date | None, Query(description="Date in YYYY-MM-DD format")] = None
):
    if (date_from is None) != (date_to is None):
        exceptions.raise_400_bad_request("Both or none dates are required.")

    if not date_from and not date_to:
        """If no dates are provided, set them to the last available date"""
        response = request("get", url=f"{NBP_API_TABLES_URL}/last").json()
        date_from = date_to = date.fromisoformat(response[0].get("effectiveDate"))

    if date_from > date_to:
        exceptions.raise_400_bad_request("The beginning date cannot be older than the end date.")

    if date_from > date.today() or date_to > date.today():
        exceptions.raise_400_bad_request("Date cannot be in the future.")

    if (date_to - date_from).days > REQUEST_LIMIT_PERIOD:
        exceptions.raise_400_bad_request("The period cannot be longer than 366 days.")

    new_rates = []
    urls = []
    existing_rates = queries.get_rates(db, date_from, date_to)

    # Split dates into periods, if request period is longer than 90 days (to avoid limitation of NBP API)
    if (date_to - date_from).days > TABLE_SPLIT_PERIOD:
        date_periods = services.split_fetch_period(date_from, date_to, TABLE_SPLIT_PERIOD)
        for date_period in date_periods:
            urls.append(f"{NBP_API_TABLES_URL}/{date_period[0]}/{date_period[1]}")
    else:
        urls.append(f"{NBP_API_TABLES_URL}/{date_from}/{date_to}")

    for url in urls:
        new_rates.extend(services.get_new_rates(request("get", url), existing_rates))

    if len(new_rates) == 0:
        exceptions.raise_400_bad_request("All rates for specified period are already in the database.")
    queries.add_rates_to_db(db, new_rates)
    return {"message": f"Added {len(new_rates)} rates"}


@router.post("/fetch/rates")
async def download_rates_for_currency(
        db: Annotated[Session, Depends(get_db)],
        code: str = Query(..., description="Currency code"),
        date_from: Annotated[date | None, Query(description="Date in YYYY-MM-DD format")] = None,
        date_to: Annotated[date | None, Query(description="Date in YYYY-MM-DD format")] = None
):
    if (date_from is None) != (date_to is None):
        exceptions.raise_400_bad_request("Both or none dates are required.")

    if not date_from and not date_to:
        """If no dates are provided, set them to the last available date"""
        url = f"{NBP_API_RATES_URL}/{code}/last"
        date_from = date_to = date.fromisoformat(request("get", url).json().get("rates")[0].get("effectiveDate"))

    if date_from > date_to:
        exceptions.raise_400_bad_request("The beginning date cannot be older than the end date.")

    if date_from > date.today() or date_to > date.today():
        exceptions.raise_400_bad_request("Date cannot be in the future.")

    if (date_to - date_from).days > REQUEST_LIMIT_PERIOD:
        exceptions.raise_400_bad_request("The period cannot be longer than 366 days.")

    code = code.upper()
    existing_rates = queries.get_code_rates(db, code, date_from, date_to)
    url = f"{NBP_API_RATES_URL}/{code}/{date_from}/{date_to}"
    new_rates = services.get_new_code_rates(request("get", url), code, existing_rates)

    if len(new_rates) == 0:
        exceptions.raise_400_bad_request(f"All {code} rates for specified period are already in the database.")
    queries.add_rates_to_db(db, new_rates)
    return {"message": f"Added {len(new_rates)} rates"}
