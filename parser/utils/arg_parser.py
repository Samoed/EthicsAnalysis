import argparse

from utils.base_parser import BaseParser


def parse_args() -> type[BaseParser]:
    """
    Init ArgumentParser
    """
    parser = argparse.ArgumentParser(description="CLI for banks")
    parser.add_argument(
        "--site",
        choices=["sravni_reviews", "banki_reviews"],
        help="site arguments",
        required=True,
    )
    return _get_class(parser.parse_args())


def _get_class(args: argparse.Namespace) -> type[BaseParser]:
    site = args.site
    match site:
        case "sravni_reviews":
            from sravni_reviews.sravni_reviews import SravniReviews

            return SravniReviews
        case "banki_reviews":
            from banki_ru_reviews.reviews_parser import BankiReviews

            return BankiReviews
        case _:
            raise ValueError("Unknown site")