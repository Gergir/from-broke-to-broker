from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from main import app
from models import Rate
from services.db_service import get_db, Base, engine


@pytest.fixture
def valid_date():
    return date(2025, 1, 22)


@pytest.fixture
def invalid_date():
    return "2025-010-22"


# Fixture to set up and tear down the database
@pytest.fixture(scope="function", autouse=True)
def setup_test_database():
    yield
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def db():
    """Provide a database session for tests."""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def mock_rates(db):
    """Add mock rates to the test database."""
    rates = [
        Rate(update_date=date(2025, 1, 23), currency="dolar amerykański", code="USD", mid=4.0124),
        Rate(update_date=date(2025, 1, 24), currency="euro", code="EUR", mid=4.21),
    ]
    db.add_all(rates)
    db.commit()
    return rates


@pytest.fixture
def mock_rates_for_fetch(db):
    data = [
        {
            "update_date": date(2025, 1, 22),
            "rates": [
                "bat (Tajlandia)",
                "dolar amerykański",
                "dolar australijski",
                "dolar Hongkongu",
                "dolar kanadyjski",
                "dolar nowozelandzki",
                "dolar singapurski",
                "euro",
                "forint (Węgry)",
                "frank szwajcarski",
                "funt szterling",
                "hrywna (Ukraina)",
                "jen (Japonia)",
                "korona czeska",
                "korona duńska",
                "korona islandzka",
                "korona norweska",
                "korona szwedzka",
                "lej rumuński",
                "lew (Bułgaria)",
                "lira turecka",
                "nowy izraelski szekel",
                "peso chilijskie",
                "peso filipińskie",
                "peso meksykańskie",
                "rand (Republika Południowej Afryki)",
                "real (Brazylia)",
                "ringgit (Malezja)",
                "rupia indonezyjska",
                "rupia indyjska",
                "won południowokoreański",
                "yuan renminbi (Chiny)",
                "SDR (MFW)"
            ]
        }
    ]
    request_date = data[0].get("update_date")
    rates = data[0].get("rates")
    for rate in rates:
        db.add(Rate(update_date=request_date, currency=rate, code="AAA", mid=1.000))
    db.commit()


client = TestClient(app)


def test_correct_get_all_currencies_with_data(mock_rates):
    response = client.get("/currencies/")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_all_currencies_empty_db():
    response = client.get("/currencies/")
    assert response.status_code == 404


def test_correct_get_rates_for_specified_date(mock_rates):
    response = client.get("/currencies/2025-01-24")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_rates_for_specified_date_empty_db():
    response = client.get("/currencies/2024-01-01")
    assert response.status_code == 404


def test_request_for_invalid_date(invalid_date, valid_date):
    future_date = date.today() + timedelta(days=1)
    response = client.get(f"/currencies/{future_date}")
    assert response.status_code == 400
    assert "Date cannot be in the future." in response.json().get("detail")

    response = client.get(f"/currencies/{invalid_date}")
    assert response.status_code == 422
    assert "Input should be a valid date" in response.json().get("detail")[0].get("msg")

    for table in ["a", "b"]:
        response = client.post(f"/currencies/fetch?table={table}&date_from={invalid_date}&date_to={valid_date}")
        assert response.status_code == 422
        assert "Input should be a valid date" in response.json().get("detail")[0].get("msg")

        response = client.post(f"/currencies/fetch?table={table}&date_from={valid_date}&date_to={future_date}")
        assert response.status_code == 400
        assert "Date cannot be in the future." in response.json().get("detail")


def test_correct_fetch_rates_period_shorten_than_90_days(valid_date):
    date_from = valid_date
    date_to = valid_date
    for table in ["a", "b"]:
        response = client.post(f"/currencies/fetch?table={table}&date_from={date_from}&date_to={date_to}")
        assert response.status_code == 200
        assert "Added" in response.json().get("message") and "rates" in response.json().get("message")


def test_correct_fetch_rates_period_longer_than_90_days(valid_date):
    date_from = valid_date - timedelta(days=91)
    for table in ["a", "b"]:
        response = client.post(f"/currencies/fetch?table={table}&date_from={date_from}&date_to={valid_date}")
        assert response.status_code == 200
        assert "Added" in response.json().get("message") and "rates" in response.json().get("message")


def test_fetch_rates_rates_for_period_already_in_db(mock_rates_for_fetch, valid_date):
    for table in ["a"]:
        response = client.post(f"/currencies/fetch?table={table}&date_from={valid_date}&date_to={valid_date}")
        assert response.status_code == 400
        assert response.json().get("detail") == "All rates for specified period are already in the database."
