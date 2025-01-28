from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from main import app
from models import Rate
from services.db_service import get_db, Base, engine


@pytest.fixture
def valid_date():
    return


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
        Rate(update_date=date(2025, 1, 23), currency="euro", code="EUR", mid=4.21),
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


@pytest.fixture
def get_dates():
    return {"valid": date(2025, 1, 22), "invalid": "2025-010-22", "future": date.today() + timedelta(days=1)}


@pytest.fixture
def valid_urls_for_get_rates():
    return ["/currencies/2025", "/currencies/2025-Q1", "/currencies/2025-01", "/currencies/2025-01-23"]


@pytest.fixture
def empty_valid_urls_for_get_rates():
    return ["/currencies/2024", "/currencies/2024-Q1", "/currencies/2024-01", "/currencies/2024-01-24"]


client = TestClient(app)


def test_get_currencies(mock_rates):
    response = client.get("/currencies/")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_currencies_empty_db():
    response = client.get("/currencies/")
    assert response.status_code == 404


def test_get_rates(mock_rates, valid_urls_for_get_rates):
    for url in valid_urls_for_get_rates:
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.json()) > 0


def test_get_rates_code(mock_rates, valid_urls_for_get_rates):
    for url in valid_urls_for_get_rates:
        for code in ["USD", "usd"]:
            response = client.get(f"{url}?code={code}")
            assert response.status_code == 200
            assert len(response.json()) > 0


def test_get_rates_empty_db(empty_valid_urls_for_get_rates):
    for url in empty_valid_urls_for_get_rates:
        response = client.get(url)
        assert response.status_code == 404
        assert "No rates found for the requested period." in response.json().get("detail")


def test_get_rates_code_empty_db(empty_valid_urls_for_get_rates):
    for url in empty_valid_urls_for_get_rates:
        for code in ["USD", "usd"]:
            response = client.get(url, params={"code": code})
            assert response.status_code == 404
            assert f"No {code.upper()} rates found for the requested period." in response.json().get("detail")


def test_get_rates_invalid_date(invalid_date):
    future_date = date.today() + timedelta(days=1)
    response = client.get(f"/currencies/{invalid_date}")
    assert response.status_code == 400
    assert "Invalid date format" in response.json().get("detail")

    response = client.get(f"/currencies/{future_date}")
    assert response.status_code == 400
    assert "Date cannot be in the future." in response.json().get("detail")


def test_fetch_table(get_dates):
    response = client.post("/currencies/fetch/tables")
    assert response.status_code == 200
    assert "Added" in response.json()["message"]

    valid_date = get_dates.get("valid")
    date_to = valid_date

    for past_date in [valid_date - timedelta(days=7), valid_date - timedelta(days=180)]:
        response = client.post("/currencies/fetch/tables", params={"date_from": past_date, "date_to": date_to})
        assert response.status_code == 200
        assert "Added" in response.json()["message"]


def test_fetch_rates(get_dates):
    params = {"code": "USD"}
    response = client.post("/currencies/fetch/rates", params=params)
    assert response.status_code == 200
    assert "Added" in response.json()["message"]

    valid_date = get_dates.get("valid")
    date_to = valid_date
    past_date = valid_date - timedelta(days=7)

    params.update({"date_from": past_date, "date_to": date_to})
    response = client.post("/currencies/fetch/rates", params=params)
    assert response.status_code == 200
    assert "Added" in response.json()["message"]


def test_fetch_rates_case_insensitive(get_dates):
    valid_date = get_dates.get("valid")
    for index, code in enumerate(["usd", "USD", "UsD"]):
        params = {"code": code, "date_from": valid_date, "date_to": valid_date}
        response = client.post("/currencies/fetch/rates", params=params)
        if index == 0:
            assert response.status_code == 200
            assert response.json()["message"] == "Added 1 rates"
        else:
            assert response.status_code == 400
            assert "already in the database" in response.json()["detail"]


def test_fetch_invalid_dates(get_dates):
    urls = ["/currencies/fetch/tables", "/currencies/fetch/rates"]
    future_date = get_dates.get("future")
    invalid_date = get_dates.get("invalid")
    valid_date = get_dates.get("valid")
    for url in urls:
        if "rates" in url:
            params = {"code": "USD"}
        else:
            params = {}

        params.update({"date_from": valid_date})
        response = client.post(url, params=params)
        assert response.status_code == 400
        assert "Both or none dates are required." in response.json()["detail"]

        params.update({"date_from": valid_date, "date_to": future_date})
        response = client.post(url, params=params)
        assert response.status_code == 400
        assert "Date cannot be in the future." in response.json()["detail"]

        params.update({"date_from": date.today(), "date_to": valid_date})
        response = client.post(url, params=params)
        assert response.status_code == 400
        assert "The beginning date cannot be older than the end date." in response.json()["detail"]

        params.update({"date_from": valid_date, "date_to": invalid_date})
        response = client.post(url, params=params)
        assert response.status_code == 422
        assert "Input should be a valid date or datetime" in response.json()["detail"][0]["msg"]

        date_over_year_in_the_past = valid_date - timedelta(days=380)
        params.update({"date_from": date_over_year_in_the_past, "date_to": valid_date})
        response = client.post(url, params=params)
        assert response.status_code == 400
        assert "The period cannot be longer than 366 days." in response.json()["detail"]


def test_fetch_all_data_already_in_db(get_dates):
    valid_date = get_dates.get("valid")
    for index, url in enumerate(["/currencies/fetch/tables", "/currencies/fetch/rates"]):
        if "rates" in url:
            params = {"code": "UsD"}
        else:
            params = {}
        params.update({"date_from": valid_date, "date_to": valid_date})
        response = client.post(url, params=params)
        if index == 0:
            assert response.status_code == 200
            assert "Added" in response.json()["message"]
        else:
            assert response.status_code == 400
            assert "are already in the database." in response.json()["detail"]
