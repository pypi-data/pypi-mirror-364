import io
import re
import requests
import pdfplumber

from bs4 import BeautifulSoup
from pdfplumber.page import Page
from urllib.parse import urlparse

from typing import Iterator


def read_web_pdf_pages(resp: requests.Response) -> Iterator[Page] | None:
    if resp.status_code > 400:
        return None

    pdf_file = io.BytesIO(resp.content)
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            yield page


def get_web_pdf_size(url: str) -> int | None:
    response = requests.head(url)
    if response.status_code >= 400:
        return None

    if "Content-Length" in response.headers:
        return int(response.headers["Content-Length"])  # Size in bytes

    return None


def get_host_url(url: str) -> str:
    parsed_url = urlparse(url)
    host = f"{parsed_url.scheme}://{parsed_url.netloc}"

    return host


def compress_soup_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "nav"]):
        tag.decompose()

    text: str = soup.text
    text = re.sub(r'\n{4,}', '\n\n\n', text)

    return text.strip()
