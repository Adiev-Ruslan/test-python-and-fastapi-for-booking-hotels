"""change fields in models\rooms.py (again)

Revision ID: 0801374dce5d
Revises: 278bdbc8ebf2
Create Date: 2025-01-15 16:36:33.679171

"""

from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0801374dce5d"
down_revision: Union[str, None] = "278bdbc8ebf2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("uq_hotel_room", "rooms", ["hotel_id", "room_num"])
    

def downgrade() -> None:
    op.drop_constraint("uq_hotel_room", "rooms", type_="unique")
    