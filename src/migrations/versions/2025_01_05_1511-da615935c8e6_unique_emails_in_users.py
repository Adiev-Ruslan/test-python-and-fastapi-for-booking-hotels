"""unique emails in users

Revision ID: da615935c8e6
Revises: 5de53afab99e
Create Date: 2025-01-05 15:11:10.373489

"""

from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "da615935c8e6"
down_revision: Union[str, None] = "5de53afab99e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(None, "users", ["email"])


def downgrade() -> None:
    op.drop_constraint(None, "users", type_="unique")
