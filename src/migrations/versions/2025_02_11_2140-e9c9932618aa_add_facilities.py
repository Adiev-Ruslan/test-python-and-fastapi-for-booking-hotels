"""add facilities

Revision ID: e9c9932618aa
Revises: 3f3b633ed07d
Create Date: 2025-02-11 21:40:07.496270

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e9c9932618aa"
down_revision: Union[str, None] = "3f3b633ed07d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "facilities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rooms_facilities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("facility_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["facility_id"],
            ["facilities.id"],
        ),
        sa.ForeignKeyConstraint(
            ["room_id"],
            ["rooms.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    

def downgrade() -> None:
    op.drop_table("rooms_facilities")
    op.drop_table("facilities")
    