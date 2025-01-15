from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint

from src.database import Base


class RoomsOrm(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    is_occupied: Mapped[bool]
    room_num: Mapped[int]
    room_type: Mapped[str]
    price: Mapped[int]
    quantity: Mapped[int]

    __table_args__ = (
        UniqueConstraint("hotel_id", "room_num", name="uq_hotel_room"),
    )
    