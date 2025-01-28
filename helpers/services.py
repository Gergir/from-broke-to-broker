from datetime import date, timedelta
from json import JSONDecodeError

from fastapi import HTTPException
from requests import Response

from models import Rate


def parse_json_response(response: Response) -> dict:
    """Parse JSON response or raise an exception if the response is not JSON."""
    try:
        return response.json()
    except JSONDecodeError:
        error_message = response.text
        error_code = response.status_code
        raise HTTPException(status_code=error_code, detail=error_message)


def split_fetch_period(start_date: date, end_date: date, split_period=90) -> list[tuple[date, date]]:
    """Split the period between start_date and end_date into smaller periods defined by split_period."""
    date_periods = []
    current_start = start_date
    while current_start < end_date:
        current_end = min(current_start + timedelta(days=split_period - 1), end_date)
        date_periods.append((current_start, current_end))
        current_start = current_end + timedelta(days=1)

    return date_periods


def get_new_rates(response: Response, rates_to_compare: set[tuple[date, str]]) -> list[Rate]:
    """Extract new rates from the response and compare them with the existing ones. Return only new rates."""
    data = parse_json_response(response)
    new_rates = []
    if not rates_to_compare:
        rates_to_compare = set()

    for record in data:
        rates_date = date.fromisoformat(record.get("effectiveDate"))
        rates = record.get("rates")

        new_rates.extend([
            Rate(**rate, update_date=rates_date) for rate in rates
            if (rates_date, rate.get("code")) not in rates_to_compare
        ])

    return new_rates


def get_new_code_rates(response: Response, code: str, rates_to_compare: set[tuple[date, float]]) -> list[Rate]:
    """Extract new code-based rates from the response and compare them with the existing ones. Return only new rates."""
    data = parse_json_response(response)
    new_rates = []
    if not rates_to_compare:
        rates_to_compare = set()

    dates_in_compare = {rate[0] for rate in rates_to_compare}  # Extract only dates, because we don't need mid

    currency = data.get("currency")
    for rate in data.get("rates"):
        rate_date = date.fromisoformat(rate.get("effectiveDate"))
        print(type(rate_date))
        mid = rate.get("mid")
        print(rate_date, rates_to_compare)
        if rate_date not in dates_in_compare:
            new_rates.append(Rate(currency=currency, code=code, mid=mid, update_date=rate_date))

    return new_rates
