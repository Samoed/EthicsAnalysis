import json
import re
from datetime import datetime
from typing import Any

import requests
from bs4 import BeautifulSoup

from banki_ru.database import BankiRuBank
from banki_ru.queries import get_bank_list
from banki_ru.schemes import BankTypes
from common import api
from common.base_parser import BaseParser
from common.schemes import (
    PatchSource,
    Source,
    SourceRequest,
    SourceTypes,
    Text,
    TextRequest,
)


class BankiBase(BaseParser):
    headers = {"X-Requested-With": "XMLHttpRequest"}
    bank_site: BankTypes
    source_type: SourceTypes

    def __init__(self) -> None:
        self.bank_list = get_bank_list(self.bank_site)
        self.source = self.create_source()
        if len(self.bank_list) == 0:
            self.load_bank_list()
            self.bank_list = get_bank_list(self.bank_site)

    def create_source(self) -> Source:
        create_source = SourceRequest(site=self.bank_site, source_type=self.source_type)
        self.logger.debug(f"Creating source {create_source}")
        return api.send_source(create_source)

    def load_bank_list(self) -> None:
        raise NotImplementedError

    def get_pages_num_html(self, url: str) -> int | None:
        response = self.send_get_request(url)
        if response.status_code != 200:
            return None
        page = BeautifulSoup(response.text, "html.parser")
        items_num_text = page.find("div", class_="ui-pagination__description")
        if items_num_text is None:
            return 1
        items_num = [int(num) for num in re.findall("\\d+", items_num_text.text)]
        # items num text pattern 1-10 из 100 -> [1, 10, 100] -> 100 / (10 - 1)
        return items_num[2] // (items_num[1] - items_num[0] + 1) + 1

    def send_get_request(
        self, url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
    ) -> requests.Response:
        if params is None:
            params = {}
        if header is None:
            header = {}
        header |= self.headers
        return super().send_get_request(url, params, header)

    def get_json_from_url(
        self, url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        if params is None:
            params = {}
        if header is None:
            header = {}
        header |= {"x-requested-with": "XMLHttpRequest"}
        return super().get_json_from_url(url, params, header)

    def get_page_from_url(
        self, url: str, params: dict[str, Any] | None = None, header: dict[str, Any] | None = None
    ) -> BeautifulSoup | None:
        if params is None:
            params = {}
        if header is None:
            header = {}
        header |= self.headers
        return super().get_page_from_url(url, params, header)

    def parse(self) -> None:
        self.logger.info(f"start parse banki.ru {self.source_type} {self.bank_site}")
        start_time = datetime.now()
        current_source = api.get_source_by_id(self.source.id)  # type: ignore
        parsed_bank_page, parsed_bank_id, parsed_time = self.get_source_params(current_source)
        for bank_index, bank in enumerate(self.bank_list):
            self.logger.info(f"[{bank_index+1}/{len(self.bank_list)}] Start parse bank {bank.bank_name}")
            if bank.bank_id < parsed_bank_id:
                continue
            start = 1
            if bank.bank_id == parsed_bank_id:
                start = parsed_bank_page + 1
            total_page = self.get_pages_num(bank)
            if total_page is None:
                continue
            for i in range(start, total_page + 1):
                self.logger.info(f"[{i}/{total_page}] start parse {bank.bank_name} reviews page {i}")
                reviews_list = self.get_page_bank_reviews(bank, i, parsed_time)
                if reviews_list is None:
                    break
                if len(reviews_list) == 0:
                    break

                api.send_texts(
                    TextRequest(
                        items=reviews_list,
                        parsed_state=json.dumps({"bank_id": bank.bank_id, "page_num": i}),
                        last_update=parsed_time,
                    )
                )

        self.logger.info(f"finish parse {self.source_type} {self.bank_site}")
        patch_source = PatchSource(last_update=start_time)
        self.source = api.patch_source(self.source.id, patch_source)  # type: ignore

    def get_pages_num(self, bank: BankiRuBank) -> int | None:
        raise NotImplementedError

    def get_page_bank_reviews(self, bank: BankiRuBank, page_num: int, parsed_time: datetime) -> list[Text] | None:
        raise NotImplementedError
