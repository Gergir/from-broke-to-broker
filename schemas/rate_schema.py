from datetime import date

from pydantic import BaseModel, Field


class RateRequestSchema(BaseModel):
    update_date: date = Field()
    currency: str = Field()
    code: str = Field(min_length=3, max_length=3)
    country: str = Field()
    mid: float = Field(gt=0)
