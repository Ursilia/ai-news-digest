"""fix created_at server default

Revision ID: cc9fb2067aa4
Revises: 02c7acb0305a
Create Date: 2026-09-03 20:17:38.144614

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc9fb2067aa4'
down_revision: Union[str, Sequence[str], None] = '02c7acb0305a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "sources",
        "created_at",
        server_default=sa.text("now()"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "sources",
        "created_at",
        server_default=None,
    )
