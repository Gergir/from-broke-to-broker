from datetime import date, timedelta
from json import JSONDecodeError

from fastapi import HTTPException
from requests import Response


def split_fetch_period(start_date: date, end_date: date, split_period=90) -> list[tuple[date, date]]:
    date_periods = []
    current_start = start_date
    while current_start < end_date:
        current_end = min(current_start + timedelta(days=split_period - 1), end_date)
        date_periods.append((current_start, current_end))
        current_start = current_end + timedelta(days=1)

    return date_periods


def fetch_rates(response: Response) -> list[dict]:
    try:
        data = response.json()
    except JSONDecodeError:
        error_message = response.text
        error_code = response.status_code
        raise HTTPException(status_code=error_code,
                            detail=f"{error_message}. {'Try other dates.' if error_code == 404 else ''}")

    return data
