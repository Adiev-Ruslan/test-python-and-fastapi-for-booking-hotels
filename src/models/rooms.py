from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from src.database import Base


class RoomsOrm(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    is_occupied: Mapped[bool]
    title: Mapped[str]
    description: Mapped[str | None]
    price: Mapped[int]
    quantity: Mapped[int]
    