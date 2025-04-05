"""Убрал unique constraint из таблицы rooms

Revision ID: 6121122bb839
Revises: 00dd1ac4e3b4
Create Date: 2025-04-05 12:32:49.572090

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6121122bb839"
down_revision: Union[str, None] = "00dd1ac4e3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("uq_hotel_room", "rooms", type_="unique")
    

def downgrade() -> None:
    op.create_unique_constraint("uq_hotel_room", "rooms", ["hotel_id"])
    