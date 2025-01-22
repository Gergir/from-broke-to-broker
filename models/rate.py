from datetime import date

from sqlalchemy.orm import Mapped, mapped_column

from services.db_service import Base


class Rate(Base):
    __tablename__ = 'rates'
    id: Mapped[int] = mapped_column(primary_key=True)
    update_date: Mapped[date] = mapped_column()
    currency: Mapped[str] = mapped_column()
    code: Mapped[str] = mapped_column()
    country: Mapped[str] = mapped_column()
    mid: Mapped[float] = mapped_column()
