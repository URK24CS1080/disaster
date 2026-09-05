"""Remove persistent account lockout state.

Revision ID: 20260905_07
Revises: 20260729_06
Create Date: 2026-09-05
"""

from alembic import op
import sqlalchemy as sa


revision = "20260905_07"
down_revision = "20260729_06"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("account_security")}
    if not ({"failed_login_attempts", "locked_until"} & columns):
        return

    indexes = {index["name"] for index in sa.inspect(bind).get_indexes("account_security")}
    with op.batch_alter_table("account_security", schema=None) as batch_op:
        if "ix_account_security_locked_until" in indexes:
            batch_op.drop_index("ix_account_security_locked_until")
        if "failed_login_attempts" in columns:
            batch_op.drop_column("failed_login_attempts")
        if "locked_until" in columns:
            batch_op.drop_column("locked_until")


def downgrade():
    with op.batch_alter_table("account_security", schema=None) as batch_op:
        batch_op.add_column(sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))
        batch_op.create_index("ix_account_security_locked_until", ["locked_until"], unique=False)
