import requests

from bs4 import BeautifulSoup
from agentwebsearch.webscraper.base import BaseWebScraper, WebPageResult
from agentwebsearch.webscraper import utils
from agentwebsearch.logger import logger


class DefaultWebScraper(BaseWebScraper):
    def scrape(self, url: str, timeout: int = 15) -> WebPageResult:
        try:
            resp = requests.get(url, timeout=timeout)
        except Exception as e:
            msg = f"Error by handling url {url}: {str(e)}"
            logger.warning(msg)
            logger.warning(e, exc_info=True)
            return self._empty_result(url)

        if resp.status_code != 200:
            return self._empty_result(url)

        soup = BeautifulSoup(resp.text, features="html.parser")
        result = self._prepare_page_result(url, soup)

        return result

    def _prepare_page_result(self, url: str, soup: BeautifulSoup) -> WebPageResult:
        a_tags = [a_tag for a_tag in soup.find_all("a", href=True)]
        links, doc_links = self._extract_links(url, a_tags)
        text = utils.compress_soup_text(soup)

        return WebPageResult(
            url=url,
            content=text,
            links=links,
            document_links=doc_links
        )

    def _extract_links(self, url: str, a_tags: list[dict]) -> tuple[list[str], list[str]]:
        host_url = utils.get_host_url(url)

        doc_links = []
        links = []
        for a in a_tags:
            href: str = a["href"]

            if ".pdf" in href:
                doc_links.append(self._prepare_pdf_link(host_url, href))
                continue

            if not href.startswith("http"):
                continue

            links.append(href)

        return links, doc_links

    def _prepare_pdf_link(self, host_url: str, url: str) -> str:
        if not url.startswith("http"):
            return host_url + url
        return url

    def _empty_result(self, url: str) -> WebPageResult:
        return WebPageResult(
            url=url,
            content=None,
            links=None,
            document_links=None
        )
