from datetime import date

from sqlalchemy.orm import Session

from models import Rate


def get_currencies(db: Session) -> list[dict[str, str]]:
    currencies = db.query(Rate.currency, Rate.code).distinct().order_by(Rate.currency).all()
    return [{"currency": currency, "code": code} for currency, code in currencies]


def get_rates(db: Session, date_from: date, date_to: date) -> set[tuple[date, str]]:
    existing_rates = db.query(Rate.update_date, Rate.code).filter(Rate.update_date.between(date_from, date_to)).all()
    return {(rate.update_date, rate.code) for rate in existing_rates}


def get_code_rates(db: Session, code: str, date_from: date, date_to: date) -> set[tuple[date, float]]:
    existing_rates = db.query(Rate.update_date, Rate.mid).filter(
        Rate.update_date.between(date_from, date_to), Rate.code == code
    ).all()
    return {(rate.update_date, rate.mid) for rate in existing_rates}


def get_rates_for_date(db: Session, request_date: date, code: str | None = None) -> list:
    if code:
        return db.query(Rate).filter(Rate.update_date == request_date, Rate.code == code).all()
    return db.query(Rate).filter(Rate.update_date == request_date).all()


def get_rates_for_period(db: Session, start_date: date, end_date: date, code: str | None = None) -> tuple[
    list[Rate], date, date]:
    query = db.query(Rate)

    if start_date == end_date:
        query = query.filter(Rate.update_date == start_date)
    else:
        query = query.filter(Rate.update_date.between(start_date, end_date))

    if code:
        query = query.filter(Rate.code == code)

    results = query.order_by(Rate.update_date).all()

    return results, start_date, end_date


def add_rates_to_db(db: Session, rates: list[Rate]) -> None:
    """Add multiple rates to the database in a single transaction."""
    db.add_all(rates)
    db.commit()
