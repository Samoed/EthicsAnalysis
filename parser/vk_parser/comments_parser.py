import json
import os
import re
from datetime import datetime
from math import ceil
from time import sleep
from typing import Any

import numpy as np

from common import api
from common.base_parser import BaseParser
from common.settings import Settings
from common.shemes import PatchSource, Source, SourceRequest, Text, TextRequest
from utils import relative_path
from utils.logger import get_logger
from vk_parser.database import VkBank
from vk_parser.queries import create_banks, get_bank_list


def clean_text_from_vk_url(match: re.Match[str]) -> str:
    group = match.group()
    return group.split("|")[1][:-1]


emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F1F2-\U0001F1F4"  # Macau flag
    "\U0001F1E6-\U0001F1FF"  # flags
    "\U0001F600-\U0001F64F"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U0001F1F2"
    "\U0001F1F4"
    "\U0001F620"
    "\u200d"
    "\u2640-\u2642"
    "\u1F91D"
    "]+",
    flags=re.UNICODE,
)


class VKParser(BaseParser):
    logger = get_logger(__name__, Settings().logger_level)
    VERSION = "5.131"

    def __init__(self) -> None:
        self.logger.info("init vk parser")
        source_create = SourceRequest(site="vk.com/comments", source_type="vk.com")
        self.source = api.send_source(source_create)
        self.bank_list = get_bank_list()
        if len(self.bank_list) == 0:
            self.load_bank_list()
            self.bank_list = get_bank_list()

    def load_bank_list(self) -> None:
        path = relative_path(os.path.dirname(__file__), "vk_bank_list.npy")
        if not os.path.exists(path):
            raise FileNotFoundError("vk_bank_list.npy not found")
        bank_arr = np.load(path, allow_pickle=True)
        db_banks = [VkBank(id=bank[0], name=bank[1], vk_id=bank[2], domain=bank[3]) for bank in bank_arr]
        create_banks(db_banks)
        self.logger.info("bank list loaded")

    def json_to_comment_text(self, domain: str, comment: dict[str, Any], bank_id: int, is_thread: bool = False) -> Text:
        if is_thread:
            url = f"https://vk.com/wall{comment['owner_id']}_{comment['post_id']}?reply={comment['id']}&thread={comment['parents_stack'][0]}"
        else:
            url = f"https://vk.com/{domain}?w=wall{comment['owner_id']}_{comment['post_id']}_r{comment['id']}"
        comment_text = re.sub(r"\[.+?\|.+?]", clean_text_from_vk_url, comment["text"])
        comment_text = emoji_pattern.sub("", comment_text)
        return Text(
            date=comment["date"], text=comment_text, link=url, source_id=self.source.id, title="", bank_id=bank_id
        )

    def get_post_comments(
        self, domain: str, owner_id: str, post_id: str, comments_num: int, bank_id: int, parsed_time: datetime
    ) -> list[Text]:
        comments_pages = ceil(comments_num / 100)
        comments = []
        params = {
            "access_token": self.settings.vk_token,
            "v": self.VERSION,
            "count": 100,
            "owner_id": owner_id,
            "post_id": post_id,
            "start_comment_id": None,
            "sort": "desc",
            "thread_items_count": 10,
        }
        for i in range(comments_pages):
            params["offset"] = i * 100
            response = self.send_get_request("https://api.vk.com/method/wall.getComments", params=params)
            comments_json = self.get_json(response)
            if comments_json is None:
                continue
            sleep(0.3)  # https://vk.com/dev/api_requests
            for comment in comments_json["response"]["items"]:
                if comment["text"] != "":
                    json_comment = self.json_to_comment_text(domain, comment, bank_id)
                    if len(json_comment.text) > 100 and json_comment.date > parsed_time:
                        comments.append(json_comment)
                for thread_comment in comment["thread"]["items"]:
                    if thread_comment["text"] != "":
                        json_comment = self.json_to_comment_text(domain, thread_comment, bank_id)
                        if len(json_comment.text) > 100 and json_comment.date > parsed_time:
                            comments.append(json_comment)
        return comments

    def get_source_params(self, source: Source) -> tuple[int, int, datetime]:
        _, parsed_bank_id, parsed_time = super().get_source_params(source)
        parsed_state = {}
        if source.parser_state is not None:
            parsed_state = json.loads(source.parser_state)
        post_id = int(parsed_state.get("post_id", "0"))
        return parsed_bank_id, post_id, parsed_time

    def parse(self) -> None:
        self.logger.info("start parse VK")
        start_time = datetime.now()
        current_source = api.get_source_by_id(self.source.id)  # type: ignore
        parsed_bank_id, post_id, parsed_time = self.get_source_params(current_source)
        for bank_iter, bank in enumerate(self.bank_list):
            self.logger.info(f"[{bank_iter}/{len(self.bank_list)}] start parse {bank.name}")
            if bank.id <= parsed_bank_id:  # type: ignore
                continue
            params_wall_get = {
                "access_token": self.settings.vk_token,
                "v": self.VERSION,
                "owner_id": bank.vk_id,
                "count": 1,
                "offset": 0,
            }
            response = self.send_get_request(
                "https://api.vk.com/method/wall.get", params=params_wall_get
            )  # get total number of posts
            response_json = self.get_json(response)
            if response_json is None:
                continue
            num_page = ceil(response_json["response"]["count"] / 100)
            params_wall_get["count"] = 100
            for i in range(num_page):
                self.logger.info(f"Start parse {bank.name} page [{i}/{num_page}]")
                params_wall_get["offset"] = i * 100
                response = self.send_get_request("https://api.vk.com/method/wall.get", params=params_wall_get)
                response_json = self.get_json(response)
                if response_json is None:
                    continue
                posts_dates = [post["date"] for post in response_json["response"]["items"]]
                if max(posts_dates) < parsed_time.timestamp():
                    break
                for post in response_json["response"]["items"]:
                    if (
                        post.get("owner_id", False)
                        or post.get("id", False)
                        or post.get("comments")
                        or post["comments"].get("count", False)
                    ):
                        continue
                    comments = self.get_post_comments(
                        bank.domain, post["owner_id"], post["id"], post["comments"]["count"], bank.id, parsed_time  # type: ignore
                    )
                    comments_date = [comment.date for comment in comments]
                    if max(comments_date) < parsed_time:
                        break
                    api.send_texts(
                        TextRequest(
                            items=comments,
                            parsed_state=json.dumps({"bank_id": bank.id, "post_id": post["id"]}),
                            last_update=parsed_time,
                        )
                    )
        patch_source = PatchSource(last_update=start_time)
        self.source = api.patch_source(self.source.id, patch_source)  # type: ignore