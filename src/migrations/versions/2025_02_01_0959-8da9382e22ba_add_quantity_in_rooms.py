"""add quantity in rooms

Revision ID: 8da9382e22ba
Revises: 559840db3530
Create Date: 2025-02-01 09:59:13.790544

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8da9382e22ba"
down_revision: Union[str, None] = "559840db3530"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("rooms", sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("rooms", "quantity", server_default=None)
    

def downgrade() -> None:
    op.drop_column("rooms", "quantity")
    