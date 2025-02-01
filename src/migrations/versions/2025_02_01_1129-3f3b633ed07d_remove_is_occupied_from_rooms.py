"""remove is_occupied from rooms

Revision ID: 3f3b633ed07d
Revises: 8da9382e22ba
Create Date: 2025-02-01 11:29:35.474269

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3f3b633ed07d"
down_revision: Union[str, None] = "8da9382e22ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("rooms", "is_occupied")
    

def downgrade() -> None:
    op.add_column(
        "rooms",
        sa.Column("is_occupied", sa.BOOLEAN(), autoincrement=False, nullable=False),
    )
    