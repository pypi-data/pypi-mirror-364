from bs4 import BeautifulSoup
from agentwebsearch.webscraper.utils import get_host_url, compress_soup_text


def test_get_host_url():
    url = "https://www.example.com/path/page.html?query=1"
    host = get_host_url(url)
    assert host == "https://www.example.com"

    url2 = "http://test.org:8080/some/path"
    host2 = get_host_url(url2)
    assert host2 == "http://test.org:8080"


def test_compress_soup_text_removes_tags_and_compresses_newlines():
    html = """
    <html>
        <head>
            <style>body {color: red;}</style>
            <script>console.log("hi")</script>
        </head>
        <body>
            <nav>Navigation</nav>
            <noscript>Fallback</noscript>
            <div>Text1</div>
            <div>Text2</div>



            <div>Text3</div>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    text = compress_soup_text(soup)
    assert "Navigation" not in text
    assert "Fallback" not in text
    assert "body {color: red;}" not in text
    assert "console.log" not in text
    assert "Text1" in text
    assert "Text2" in text
    assert "Text3" in text
    # Check that excessive newlines are compressed
    assert "\n\n\n" not in text
