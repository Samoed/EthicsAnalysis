"""empty message

Revision ID: bbe02e3aceee
Revises: 3a79a22b07ba
Create Date: 2022-11-10 00:33:32.129632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bbe02e3aceee'
down_revision = '3a79a22b07ba'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bank', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False,
               autoincrement=True,
               existing_server_default=sa.text("nextval('bank_id_seq'::regclass)"))
    op.alter_column('text', 'bank_id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('text', 'bank_id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.alter_column('bank', 'id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               autoincrement=True,
               existing_server_default=sa.text("nextval('bank_id_seq'::regclass)"))
    # ### end Alembic commands ###
