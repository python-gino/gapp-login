"""wechat login initial

Revision ID: b5078e717ec1
Revises:
Create Date: 2020-06-18 11:13:08.088391

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b5078e717ec1"
down_revision = None
branch_labels = ("wechat",)
depends_on = "a36c9db3f264"


def upgrade():
    op.execute(
        "CREATE INDEX identities_wechat_unionid_idx "
        "    ON identities (CAST(profile ->> 'wechat_unionid' AS CHARACTER VARYING)) "
        " WHERE starts_with(idp, 'WECHAT')"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS identities_wechat_unionid_idx")
