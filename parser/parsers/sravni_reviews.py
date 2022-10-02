from datetime import datetime
from math import ceil

import requests
from requests import Response

from database.reviews_site import SravniBankInfo
from misc.logger import get_logger
from queues import api
from queues.sravni_ru import create_banks, get_bank_list
from shemes.bank import Source, SravniRuItem, Text, TextRequest


class SravniReviews:
    logger = get_logger(__name__)
    source = Source(site="sravni.ru", source_type="reviews")

    def __init__(self) -> None:
        self.bank_list = get_bank_list()
        self.source_id = api.send_source(self.source)
        if len(self.bank_list) == 0:
            self.get_bank_list()
            self.bank_list = get_bank_list()

    def request_bank_list(self) -> Response:
        data = {
            "select": [
                "oldId",
                "alias",
                "name",
                "license",
                "status",
                "ratings",
                "contacts",
                "requisites",
            ],
            "statuses": "active",
            "type": "bank",
            "limit": 1000,
            "skip": 0,
            "sort": ["-ratings", "ratings.assetsRatingPosition"],
            "location": "6.",
            "isMainList": True,
        }
        return requests.post("https://www.sravni.ru/proxy-organizations/banks/list", data=data)

    def get_bank_list(self) -> None:
        self.logger.info("start download bank list")
        self.logger.info("send request to https://www.sravni.ru/proxy-organizations/banks/list")
        request = self.request_bank_list()
        items = request.json()["items"]
        self.logger.info("finish download bank list")
        existing_banks = api.get_bank_list()
        banks_id = [bank.id for bank in existing_banks]
        sravni_bank_list = []
        for item in items:
            if item["license"] not in banks_id:
                continue
            names = item["name"]
            sravni_bank_list.append(
                SravniRuItem(
                    sravni_id=item["_id"],
                    sravni_old_id=item["oldId"],
                    alias=item["alias"],
                    bank_id=item["license"],
                    bank_name=names["short"],
                    bank_full_name=names["full"],
                    bank_official_name=names["official"],
                )
            )
        banks_db = []
        for bank in sravni_bank_list:
            banks_db.append(SravniBankInfo.from_pydantic(bank))
        create_banks(banks_db)
        self.logger.info("create main table for banks")

    def parse_reviews(
        self, reviews_array: list[dict[str, str]], last_date: datetime, bank: SravniBankInfo
    ) -> list[Text]:
        reviews = []
        for review in reviews_array:
            url = f"https://www.sravni.ru/bank/{bank.alias}/otzyvy/{review['id']}"
            # noinspection PyTypeChecker
            parsed_review = Text(
                source_id=self.source_id,
                bank_id=bank.bank_id,
                link=url,
                date=review["date"],
                title=review["title"],
                text=review["text"],
                comments_num=int(review["commentsCount"]),
            )
            if last_date > parsed_review.date.replace(tzinfo=None):
                continue
            reviews.append(parsed_review)
        return reviews

    def get_bank_info(self, bank_info: SravniBankInfo, page_num: int = 0, page_size: int = 1000) -> Response:
        response = Response()
        for _ in range(3):
            response = requests.get(
                f"https://www.sravni.ru/proxy-reviews/reviews/?filterBy=withRates&isClient=false&locationRoute=&newIds=true&orderBy=byDate&pageIndex={page_num}&pageSize={page_size}&reviewObjectId={bank_info.sravni_id}&reviewObjectType=bank&specificProductId=&tag=&withVotes=true"
            )  # todo params to dict
            if response.status_code != 500:
                return response
        return response

    def get_num_reviews(self, bank_info: SravniBankInfo) -> int:
        response = self.get_bank_info(bank_info, page_size=1)
        if response.status_code != 200:
            self.logger.error(f"error {response.status_code} for {bank_info.alias}")
            return 0
        reviews_total = int(response.json()["total"])
        return ceil(reviews_total / 1000)

    def get_reviews(self, parsed_time: datetime, bank_info: SravniBankInfo) -> list[Text]:
        reviews_array = []
        page_num = self.get_num_reviews(bank_info)
        for i in range(page_num):
            self.logger.debug(f"download page {i} for {bank_info.alias}")
            response = self.get_bank_info(bank_info, i)

            if response.status_code == 500 or response.status_code is None:
                break
            reviews_json = response.json()
            reviews = reviews_json.get("items", [])
            if len(reviews) == 0:
                break
            reviews_array.extend(reviews)

        return self.parse_reviews(reviews_array, parsed_time, bank_info)

    def parse(self) -> None:
        start_time = datetime.now()
        current_source = api.get_source_by_id(self.source_id)
        parsed_time = current_source.last_update
        if parsed_time is None:
            parsed_time = datetime.min

        for i, bank_info in enumerate(self.bank_list):
            self.logger.info(f"[{i}/{len(self.bank_list)}] download reviews for {bank_info.alias}")

            reviews = self.get_reviews(parsed_time, bank_info)
            time = datetime.now()
            api.send_texts(TextRequest(items=reviews, last_update=start_time))
            self.logger.debug(f"Time for {bank_info.alias} send reviews: {datetime.now() - time}")