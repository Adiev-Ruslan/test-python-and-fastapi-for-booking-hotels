"""удалил поле quantity в models\rooms.py

Revision ID: 90e77b124c50
Revises: 0801374dce5d
Create Date: 2025-01-17 17:42:52.715690

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "90e77b124c50"
down_revision: Union[str, None] = "0801374dce5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("rooms", "quantity")


def downgrade() -> None:
    op.add_column(
        "rooms",
        sa.Column("quantity", sa.INTEGER(), autoincrement=False, nullable=False),
    )
