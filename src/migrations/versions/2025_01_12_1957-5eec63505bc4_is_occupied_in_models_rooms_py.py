"""is_occupied in models\rooms.py

Revision ID: 5eec63505bc4
Revises: da615935c8e6
Create Date: 2025-01-12 19:57:38.384418

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5eec63505bc4"
down_revision: Union[str, None] = "da615935c8e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("rooms", sa.Column("is_occupied", sa.Boolean(), nullable=False))


def downgrade() -> None:
    op.drop_column("rooms", "is_occupied")
