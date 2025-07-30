import random
import time
from typing import Dict

from DrissionPage import ChromiumOptions
from DrissionPage import WebPage
from dataflow_sdk import save_item, Record, save_items
from dataflow_sdk.entity.model import CrawlType
from jsonpath_ng import parse
from loguru import logger


class DrissionPageBase:
    """
    redis blpop
    """

    site_name: str

    def __init__(self):
        self.page = None

    def start(self, user_data_path=None, proxy=None, is_max=True):
        co = ChromiumOptions().set_paths(user_data_path=user_data_path)
        if proxy:
            co.set_proxy(proxy)

        self.page = WebPage(chromium_options=co, session_or_options=False)
        if is_max:
            self.page.set.window.max()

    def cookies(self):
        return self.page.cookies

    def scroll(self):
        pass

    def login(self):
        pass

    def logout(self):
        pass

    def register(self):
        pass

    def html(self):
        return self.page.html

    def find_expr(self, expr, data: Dict):
        """

        :param expr:
        :param data: json类型
        :return:
        """
        jsonpath_expr = parse(expr)
        matches = jsonpath_expr.find(data)
        return matches

    def scroll_to_bottom(
            self,
            spider_url: str,
            sink_id: str = None,
            path_expr: str = None,
            key: str = None,
            detail_url: str = None,
            max_scroll: int = 100
    ):
        """
        滑动到最底部

        :param spider_url: 必传
        :param path_expr:
        :param key: 需要上报的 sink_id + pk
        :param detail_url: 点击详情页面
        :param sink_id: sink_id
        :param max_scroll:
        :return:
        """
        last_height = self.page.run_js('return document.body.scrollHeight;')
        spider_datatime = int(time.time())
        for page in range(max_scroll):
            self.page.run_js('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(random.uniform(1.5, 3))
            new_height = self.page.run_js('return document.body.scrollHeight;')
            packet = self.page.listen.wait()
            if sink_id:
                save_item(sink_id, Record(
                    crawl_type=CrawlType.LIST,
                    crawl_url=f"{packet.request.url}/{packet.request.method}/{spider_datatime}/{page}",
                    data=packet.response.body,
                    metadata=packet.request._request))

            if path_expr:
                match_result = self.find_expr(path_expr, packet.response.body)
                # item数据
                save_items(sink_id,
                           [Record(crawl_url=f"https://www.instagram.com/p/{x.value[key]}", crawl_type=CrawlType.ITEM,
                                   data=x.value)
                            for x in match_result])

            logger.info(packet.response.body)

            if path_expr and detail_url and key:
                # 是在列表采集，还是单独采集
                # https://www.instagram.com/p/DMVu06iSvMC/?img_index=1
                # 访问 -> 返回
                match_result = self.find_expr(path_expr, packet.response.body)
                for match in match_result:
                    click_url = detail_url.format(**{key: match.value[key]})
                    logger.info(f"click_url: {click_url}")

            if new_height == last_height:
                break
            last_height = new_height
