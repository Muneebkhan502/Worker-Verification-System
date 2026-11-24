"""iqama no not unique

Revision ID: e778f531d772
Revises: 511db768e153
Create Date: 2026-11-24 02:24:25.214602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e778f531d772'
down_revision: Union[str, Sequence[str], None] = '511db768e153'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.drop_index(
        'ix_workers_iqama_no',
        table_name='workers'
    )

    op.create_index(
        'ix_workers_iqama_no',
        'workers',
        ['iqama_no'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        'ix_workers_iqama_no',
        table_name='workers'
    )

    op.create_index(
        'ix_workers_iqama_no',
        'workers',
        ['iqama_no'],
        unique=True
    )
    # ### end Alembic commands ###
