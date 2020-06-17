"""wechat login initial

Revision ID: 450921ce3e56
Revises:
Create Date: 2020-06-17 15:18:58.686238

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "450921ce3e56"
down_revision = None
branch_labels = ("wechat",)
depends_on = None


def upgrade():
    op.execute(
        "CREATE INDEX identities_wechat_unionid_idx "
        "    ON identities (CAST(profile ->> 'wechat_unionid' AS CHARACTER VARYING)) "
        " WHERE CAST(profile ->> 'wechat_unionid' AS CHARACTER VARYING) IS NOT NULL"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS identities_wechat_unionid_idx")
