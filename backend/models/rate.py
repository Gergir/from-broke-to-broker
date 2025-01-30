from ast import Index
from datetime import date

from sqlalchemy.orm import Mapped, mapped_column

from services.db_service import Base


class Rate(Base):
    __tablename__ = 'rates'
    id: Mapped[int] = mapped_column(primary_key=True)
    update_date: Mapped[date] = mapped_column(index=True)
    currency: Mapped[str] = mapped_column(index=True)
    code: Mapped[str] = mapped_column(index=True)
    mid: Mapped[float] = mapped_column()

    date_code_index = Index( ("update_date", "code"), ) # Indexing together for faster search
