"""change fields in models\rooms.py

Revision ID: 278bdbc8ebf2
Revises: 5eec63505bc4
Create Date: 2025-01-13 19:02:37.513843

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "278bdbc8ebf2"
down_revision: Union[str, None] = "5eec63505bc4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("rooms", sa.Column("room_num", sa.Integer(), nullable=False))
    op.add_column("rooms", sa.Column("room_type", sa.String(), nullable=False))
    op.drop_column("rooms", "description")
    op.drop_column("rooms", "title")


def downgrade() -> None:
    op.add_column("rooms", sa.Column("title", sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column(
        "rooms",
        sa.Column("description", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_column("rooms", "room_type")
    op.drop_column("rooms", "room_num")
