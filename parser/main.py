from logging import getLogger

import schedule
from sqlalchemy_utils import create_database, database_exists

from common.base_parser import BaseParser
from common.settings import get_settings
from utils.arg_parser import parse_args
from common.database import Base, engine
from utils.logger import get_logger
from time import sleep


def parsers_setup(parser_class: type[BaseParser]) -> None:
    parser = parser_class()
    parser.parse()
    getLogger("schedule")
    schedule.every().day.do(parser.parse)
    while True:
        schedule.run_pending()


def main() -> None:
    sleep(5)
    settings = get_settings()
    logger = get_logger(__name__, settings.logger_level)
    logger.info("start app")
    parser_class = parse_args()
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(bind=engine)
    logger.info("create db")
    parsers_setup(parser_class)


if __name__ == "__main__":
    main()
