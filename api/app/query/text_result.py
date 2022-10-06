from sqlalchemy.orm import Session

from app.database.text_result import TextResult
from app.database.text_sentence import TextSentence, TempSentence
from app.schemes.text import PostTextResultItem


async def get_text_result_items(db: Session, text_id: int) -> list[TextResult]:
    query = db.query(TextResult).join(TextResult.text_sentence).filter(TextSentence.text_id == text_id)
    return query.all()


async def create_text_results(db: Session, texts: list[PostTextResultItem], table_name: str) -> None:
    text_results = []
    for text in texts:
        text_result = TextResult(
            text_sentence_id=text.text_sentence_id,
            result=text.text_result,
            model_id=text.model_id,
        )
        text_results.append(text_result)
        db.query(TempSentence).filter(TempSentence.id == text.text_sentence_id).filter(TempSentence.query == table_name).delete()
    db.add_all(text_results)
    db.commit()
