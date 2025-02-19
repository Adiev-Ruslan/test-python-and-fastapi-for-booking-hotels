"""room_type теперь необязательный параметр вRoomsOrm

Revision ID: 7cd22158182c
Revises: e9c9932618aa
Create Date: 2025-02-19 19:08:22.182344

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7cd22158182c"
down_revision: Union[str, None] = "e9c9932618aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("rooms", "room_type", existing_type=sa.VARCHAR(), nullable=True)
    

def downgrade() -> None:
    op.alter_column("rooms", "room_type", existing_type=sa.VARCHAR(), nullable=False)
    