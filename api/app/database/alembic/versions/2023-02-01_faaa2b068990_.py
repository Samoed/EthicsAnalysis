"""empty message

Revision ID: faaa2b068990
Revises: 0adc9ba23842
Create Date: 2023-02-01 14:00:59.125334

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "faaa2b068990"
down_revision = "df093a18dfdd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f("ix_text_date_extract_year"), "text", [sa.text("extract(year from date)")], unique=False)
    op.create_index(op.f("ix_text_date_extract_quarter"), "text", [sa.text("extract(quarter from date)")], unique=False)
    op.create_index(op.f("ix_text_date_trunc_month"), "text", [sa.text("date_trunc('month', date)")], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_text_date_trunc_month"), table_name="text")
    op.drop_index(op.f("ix_text_date_extract_quarter"), table_name="text")
    op.drop_index(op.f("ix_text_date_extract_year"), table_name="text")
    # ### end Alembic commands ###
