"""
drop flightNumber from passengers

Revision ID: 20240904_drop_flightnumber
Revises:
Create Date: 2025-09-04 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20240904_drop_flightnumber"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("passengers") as batch_op:
        # Drop column if exists; some DBs may error if not present
        try:
            batch_op.drop_column("flightNumber")
        except Exception:
            pass


def downgrade() -> None:
    with op.batch_alter_table("passengers") as batch_op:
        batch_op.add_column(sa.Column("flightNumber", sa.String(), nullable=True))
