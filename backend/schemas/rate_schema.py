from datetime import date

from pydantic import BaseModel


class RateResponseSchema(BaseModel):
    update_date: date
    currency: str
    code: str
    mid: float

    class ConfigDict:
        from_attributes = True


class RateResponseOnlyCurrencies(BaseModel):
    currency: str
    code: str

    class ConfigDict:
        from_attributes = True
