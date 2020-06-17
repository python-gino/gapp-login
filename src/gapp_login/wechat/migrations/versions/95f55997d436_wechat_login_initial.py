"""wechat login initial

Revision ID: 95f55997d436
Revises:
Create Date: 2020-06-17 14:07:52.112350

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "95f55997d436"
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
    op.drop_index("identities_wechat_unionid_idx", table_name="identities")
