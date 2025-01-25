from datetime import date

from pydantic import BaseModel, Field


class RateRequestSchema(BaseModel):
    update_date: date = Field()
    currency: str = Field()
    code: str = Field(min_length=3, max_length=3)
    mid: float = Field(gt=0)


class RateResponseSchema(BaseModel):
    update_date: date
    currency: str
    code: str
    mid: float

    class Config:
        from_attributes = True


class RatesOnlyResponseSchema(BaseModel):
    update_date: date
    rates: list[str]

    class Config:
        from_attributes = True
