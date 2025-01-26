from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from models import Rate


def find_all_currencies_for_all_dates(db: Session) -> list:
    """
    SQL COMMAND:
    SELECT rates.update_date AS rates_update_date, array_agg(rates.currency) AS currencies FROM rates
    GROUP BY rates.update_date ORDER BY rates.update_date
    """
    return db.query(Rate.update_date, func.array_agg(Rate.currency).label("currencies")).group_by(
        Rate.update_date).order_by(Rate.update_date).all()


def find_all_rates_for_specified_date(db: Session, request_date) -> list:
    return db.query(Rate).filter(Rate.update_date == request_date).all()


def find_rates_with_specified_code_and_date(db: Session, rates_date, currency) -> Rate | None:
    return db.query(Rate).filter(Rate.update_date == rates_date, Rate.currency == currency).first()


def find_rates_for_specified_currency_and_date(
        db: Session,
        currency: str,
        date_from: date,
        date_to: date
):
    return (
        db.query(Rate.update_date, Rate.mid)
        .filter(
            Rate.currency == currency,
            Rate.update_date.between(date_from, date_to)
        )
        .order_by(Rate.update_date)
        .all())


def add_rate_to_db(db: Session, rate: Rate) -> None:
    db.add(rate)
    db.commit()
