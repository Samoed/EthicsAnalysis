from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database.models.bank import Bank  # noqa: F401
from app.database.models.model import Model, ModelType  # noqa: F401
from app.database.models.source import Source, SourceType  # noqa: F401
from app.database.models.text import Text  # noqa: F401
from app.database.models.text_result import TextResult  # noqa: F401
from app.database.models.text_sentence import TempSentence, TextSentence  # noqa: F401
from app.settings import Settings


class SessionManager:
    """
    A class that implements the necessary functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    def __init__(self) -> None:
        self.refresh()

    def __new__(cls) -> "SessionManager":
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance  # noqa

    def get_session_maker(self) -> sessionmaker:  # type: ignore
        return sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    def refresh(self) -> None:
        self.engine = create_async_engine(Settings().database_uri, echo=True, future=True)


async def get_session() -> AsyncSession:  # type: ignore
    session_maker = SessionManager().get_session_maker()
    async with session_maker() as session:
        yield session
