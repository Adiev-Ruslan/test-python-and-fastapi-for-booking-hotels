"""relation rooms was created

Revision ID: cb69757ca4e5
Revises: 7cfa3b727002
Create Date: 2024-12-23 22:31:00.572960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb69757ca4e5'
down_revision: Union[str, None] = '7cfa3b727002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hotel_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    
def downgrade() -> None:
    op.drop_table('rooms')
    