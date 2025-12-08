import requests
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, url: str) -> None:
        self.url = url
        self._parsed_page = None

    def get_slug(self) -> str:
        return self.url.split("/")[-2]

    def parse_webpage(self) -> str:
        webpage = requests.get(self.url)
        self._parsed_page = BeautifulSoup(webpage.content, "html.parser")
        return self._parsed_page

    def scrape_content(self, html_element, attribute) -> str:
        try:
          content = self._parsed_page.find(html_element, attrs=attribute).text
        except:
          return ""

        return content

    def scrape_content_list(self, html_element, attribute) -> list[str]:
        try:
          elements = self._parsed_page.find_all(html_element, attrs=attribute)
        except:
          return []

        content_list = []
        for element in elements:
            content_list.append(element.text)

        return content_list
