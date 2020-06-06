"""initial

Revision ID: 56fd432ac572
Revises:
Create Date: 2020-06-06 14:29:07.313677

"""
import sqlalchemy as sa
from alembic import op

revision = "56fd432ac572"
down_revision = None
branch_labels = ("sms",)
depends_on = None


def upgrade():
    op.create_table(
        "login_sms",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("prefix", sa.Text(), nullable=False),
        sa.Column("number", sa.Text(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("consumed_at", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("login_sms")
