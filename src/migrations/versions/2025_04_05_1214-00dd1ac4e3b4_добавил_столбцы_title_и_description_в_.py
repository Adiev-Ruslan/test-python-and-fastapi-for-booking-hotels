"""Добавил столбцы title и description в таблицу rooms вместо ненужных

Revision ID: 00dd1ac4e3b4
Revises: 7cd22158182c
Create Date: 2025-04-05 12:14:10.157643

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "00dd1ac4e3b4"
down_revision: Union[str, None] = "7cd22158182c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rooms",
        sa.Column("title", sa.String(), nullable=False)
    )
    op.add_column(
        "rooms",
        sa.Column("description", sa.String(), nullable=True)
    )
    op.drop_constraint(
        "uq_hotel_room",
        "rooms",
        type_="unique"
    )
    op.create_unique_constraint(
        "uq_hotel_room",
        "rooms",
        ["hotel_id"]
    )
    op.drop_column("rooms", "room_num")
    op.drop_column("rooms", "room_type")
    

def downgrade() -> None:
    op.add_column(
        "rooms",
        sa.Column("room_type", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "rooms",
        sa.Column("room_num", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.drop_constraint("uq_hotel_room", "rooms", type_="unique")
    op.create_unique_constraint("uq_hotel_room", "rooms", ["hotel_id", "room_num"])
    op.drop_column("rooms", "description")
    op.drop_column("rooms", "title")
    