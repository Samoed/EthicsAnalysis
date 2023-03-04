from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import TextSentenceCount
from app.database.models import AggregateTableModelResult as TextResultAgg
from app.schemes.source import SourceSitesEnum
from app.schemes.views import (
    AggregateTextResultItem,
    IndexTypeVal,
    ReviewsCountItem,
    SentenceCountAggregate,
)


def get_index(index_type: IndexTypeVal) -> Any:
    match index_type:
        case IndexTypeVal.index_base:
            return TextResultAgg.index_base
        case IndexTypeVal.index_std:
            return TextResultAgg.index_std
        case IndexTypeVal.index_mean:
            return TextResultAgg.index_mean
        case IndexTypeVal.index_safe:
            return TextResultAgg.index_safe
        case _:
            raise ValueError


def aggregate_columns(aggregate_by_year: bool) -> list[Any]:
    if aggregate_by_year:
        aggregate_cols = [TextResultAgg.year, TextResultAgg.quater]
    else:
        aggregate_cols = [TextResultAgg.quater, TextResultAgg.year]
    aggregate_cols.extend(
        [TextResultAgg.source_type, TextResultAgg.model_name, TextResultAgg.bank_name, TextResultAgg.bank_id]
    )
    return aggregate_cols


async def aggregate_text_result(
    session: AsyncSession,
    start_year: int,
    end_year: int,
    bank_ids: list[int],
    model_names: list[str],
    source_types: list[str],
    aggregate_by_year: bool,
    index_type: IndexTypeVal,
) -> list[AggregateTextResultItem]:
    index_val = get_index(index_type)
    aggregate_cols = aggregate_columns(aggregate_by_year)
    query = (
        select(
            TextResultAgg.year,
            TextResultAgg.quater,
            TextResultAgg.bank_name,
            TextResultAgg.bank_id,
            TextResultAgg.model_name,
            TextResultAgg.source_type,
            func.sum(index_val).label("index"),
        )
        .where(
            TextResultAgg.year.between(start_year, end_year),
            TextResultAgg.model_name.in_(model_names),
            TextResultAgg.source_type.in_(source_types),
            TextResultAgg.bank_id.in_(bank_ids),
        )
        .group_by(*aggregate_cols)
        .order_by(TextResultAgg.year, TextResultAgg.quater)
    )
    return [
        AggregateTextResultItem.construct(  # don't validate data
            _fields_set=AggregateTextResultItem.__fields_set__,
            year=row["year"],
            quarter=row["quater"],
            date=date(row["year"], row["quater"] * 3, 1),
            bank_id=row["bank_id"],
            bank_name=row["bank_name"],
            model_name=row["model_name"],
            source_type=row["source_type"],
            index=row["index"],
        )
        for row in await session.execute(query)
    ]


async def text_reviews_count(
    session: AsyncSession,
    start_date: date,
    end_date: date,
    source_sites: list[SourceSitesEnum] | None,
    # sources_types: list[SourceTypesEnum],
    aggregate_by_year: SentenceCountAggregate,
) -> list[ReviewsCountItem]:
    date_label = "date_"
    match aggregate_by_year:
        case SentenceCountAggregate.month:
            query = select(
                TextSentenceCount.date.label(date_label),
                TextSentenceCount.source_site,
                TextSentenceCount.source_type,
                TextSentenceCount.count_reviews,
            )
        case SentenceCountAggregate.quarter:
            query = select(
                func.date_trunc("quarter", TextSentenceCount.date).label(date_label),
                TextSentenceCount.source_site,
                TextSentenceCount.source_type,
                func.sum(TextSentenceCount.count_reviews).label("count_reviews"),
            ).group_by(
                date_label,
                TextSentenceCount.source_site,
                TextSentenceCount.source_type,
            )
        case _:
            raise ValueError
    query = query.where(TextSentenceCount.date.between(start_date, end_date))
    if source_sites:
        query = query.where(TextSentenceCount.source_site.in_(source_sites))
    return [
        ReviewsCountItem.construct(  # don't validate data
            _fields_set=ReviewsCountItem.__fields_set__,
            date=row[date_label],
            source_site=row["source_site"],
            source_type=row["source_type"],
            count=row["count_reviews"],
        )
        for row in await session.execute(query)
    ]