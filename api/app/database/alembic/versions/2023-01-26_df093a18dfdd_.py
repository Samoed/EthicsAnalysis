"""empty message

Revision ID: df093a18dfdd
Revises: 3a9a41953764
Create Date: 2023-01-26 16:44:56.061499

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "df093a18dfdd"
down_revision = "3a9a41953764"
branch_labels = None
depends_on = None

aggregate_table_model_result = sa.Table(
    "aggregate_table_model_result",
    sa.MetaData(),
    sa.Column("id", sa.Integer),
    sa.Column("year", sa.Integer),
    sa.Column("quater", sa.Integer),
    sa.Column("model_name", sa.String),
    sa.Column("source_site", sa.String),
    sa.Column("source_type", sa.String),
    sa.Column("bank_name", sa.String),
    sa.Column("bank_id", sa.Integer),
    sa.Column("neutral", sa.Integer),
    sa.Column("positive", sa.Integer),
    sa.Column("negative", sa.Integer),
    sa.Column("total", sa.Integer),
    sa.Column("index_base", sa.Float),
    sa.Column("index_mean", sa.Float),
    sa.Column("index_std", sa.Float),
    sa.Column("index_safe", sa.Float),
)


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("aggregate_table_model_result", sa.Column("index_base", sa.Float(), nullable=True))
    op.add_column("aggregate_table_model_result", sa.Column("index_mean", sa.Float(), nullable=True))
    op.add_column("aggregate_table_model_result", sa.Column("index_std", sa.Float(), nullable=True))
    op.add_column("aggregate_table_model_result", sa.Column("index_safe", sa.Float(), nullable=True))
    # ### end Alembic commands ###
    op.execute(
        sa.update(aggregate_table_model_result)
        .where(aggregate_table_model_result.c.total > 0)
        .values(
            index_base=sa.cast(
                (aggregate_table_model_result.c.positive - aggregate_table_model_result.c.negative), sa.Float
            )
            / aggregate_table_model_result.c.total
        )
    )
    select_mean = sa.select(
        aggregate_table_model_result.c.id,
        sa.func.avg(aggregate_table_model_result.c.index_base)
        .over(partition_by=[aggregate_table_model_result.c.source_type, aggregate_table_model_result.c.model_name])
        .label("avg"),
    ).subquery("select_mean")
    op.execute(
        sa.update(aggregate_table_model_result)
        .where(aggregate_table_model_result.c.id == select_mean.c.id)
        .values(
            index_mean=select_mean.c.avg,
        )
    )
    eps = 1e-5
    # todo add test for zero division
    op.execute(
        sa.update(aggregate_table_model_result)
        .where(aggregate_table_model_result.c.total > 0)
        .values(
            # (db.POS / (db.TOTAL - db.POS) / db.TOTAL**3 + db.NEG / (db.TOTAL - db.NEG) / db.TOTAL**3)**0.5
            index_std=sa.func.sqrt(
                aggregate_table_model_result.c.positive
                / (aggregate_table_model_result.c.total - aggregate_table_model_result.c.positive + eps)
                / sa.func.pow(aggregate_table_model_result.c.total, 3)
                + aggregate_table_model_result.c.negative
                / (aggregate_table_model_result.c.total - aggregate_table_model_result.c.negative + eps)
                / sa.func.pow(aggregate_table_model_result.c.total, 3)
            ),
        )
    )

    # (2 * (db['INDEX'] - db['INDEX_MEAN'] > 0) - 1) * (np.maximum(np.abs(db['INDEX'] - db['INDEX_MEAN']) - db['INDEX_STD'],0))
    # (2 * (index_base - index_mean > 0) - 1) * (max(abs(index_base - index_mean) - index_std, 0))
    op.execute(
        sa.update(aggregate_table_model_result)
        .where(aggregate_table_model_result.c.total > 0)
        .values(
            index_safe=(
                sa.cast(
                    2
                    * sa.cast(
                        aggregate_table_model_result.c.index_base - aggregate_table_model_result.c.index_mean > 0,
                        sa.Integer,
                    )
                    - 1,
                    sa.Float,
                )
                * sa.func.greatest(
                    sa.func.abs(aggregate_table_model_result.c.index_base - aggregate_table_model_result.c.index_mean)
                    - aggregate_table_model_result.c.index_std,
                    0,
                )
            ),
        )
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("aggregate_table_model_result", "index_safe")
    op.drop_column("aggregate_table_model_result", "index_std")
    op.drop_column("aggregate_table_model_result", "index_mean")
    op.drop_column("aggregate_table_model_result", "index_base")
    # ### end Alembic commands ###
