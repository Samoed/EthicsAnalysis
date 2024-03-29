"""empty message

Revision ID: cab5f2d71e76
Revises: 56a380c80e86
Create Date: 2023-02-13 16:31:08.073884

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "cab5f2d71e76"
down_revision = "56a380c80e86"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("text_result_text_sentence_id_fkey", "text_result", type_="foreignkey")
    op.create_foreign_key(
        "text_result_text_sentence_id_fkey_cascade",
        "text_result",
        "text_sentence",
        ["text_sentence_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("text_sentence_text_id_fkey", "text_sentence", type_="foreignkey")
    op.create_foreign_key(
        "text_sentence_text_id_fkey_cascade", "text_sentence", "text", ["text_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("text_sentence_text_id_fkey_cascade", "text_sentence", type_="foreignkey")
    op.create_foreign_key("text_sentence_text_id_fkey", "text_sentence", "text", ["text_id"], ["id"])
    op.drop_constraint("text_result_text_sentence_id_fkey_cascade", "text_result", type_="foreignkey")
    op.create_foreign_key(
        "text_result_text_sentence_id_fkey", "text_result", "text_sentence", ["text_sentence_id"], ["id"]
    )
    # ### end Alembic commands ###
