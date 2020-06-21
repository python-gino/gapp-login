"""added wechat_app_id index

Revision ID: 0f656e4e6674
Revises: b5078e717ec1
Create Date: 2020-06-21 17:58:13.482104

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0f656e4e6674"
down_revision = "b5078e717ec1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "CREATE INDEX identities_wechat_app_id_idx "
        "    ON identities (CAST(profile ->> 'wechat_app_id' AS CHARACTER VARYING)) "
        " WHERE starts_with(idp, 'WECHAT')"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS identities_wechat_app_id_idx")
