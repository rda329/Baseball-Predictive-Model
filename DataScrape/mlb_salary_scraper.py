# pip install bs4 curl_cffi html5lib
import json
from typing import Union

from bs4 import BeautifulSoup
from curl_cffi import requests


class SpotracScraper:
    BASE_URL = "https://www.spotrac.com"
    PAYROLL_URL = BASE_URL + "/mlb/payroll/_/year/{year}"
    PROXIES = None
    HEADERS = {}
    COOKIES = {}

    def __init__(self, headers: Union[None, dict], proxy: Union[str, None] = None):
        self.headers = headers
        if proxy:
            self.PROXIES = {"http": proxy, "https": proxy}

        if headers:
            self.HEADERS.update(headers)

        # init with cookies
        self.get_cookies()

    def get_cookies(self):
        """ we can get cookies just visiting google.com """
        response = requests.get(self.BASE_URL, impersonate="chrome131", verify=False, proxies=self.PROXIES,
                                headers=self.HEADERS)
        self.COOKIES = response.cookies.get_dict()

    def get_salaries(self, year_start: int, year_end: int):
        """ get salaries between years """

        all_salaries = {}
        for year in range(year_start, year_end + 1):
            params = {}
            url = self.PAYROLL_URL.format(year=year)
            response = requests.post(
                url, impersonate="chrome131", verify=False, proxies=self.PROXIES, headers=self.HEADERS,
                cookies=self.COOKIES, params=params, data={"ajax": "true"}
            )

            if response.status_code != 200:
                print(f"Year {year} failed status code: {response.status_code}")

            salaries = self.parse_salaries(response)
            all_salaries[str(year)] = salaries
            print(f"Year {year} scraped")

        print(f"done. extracted salaries: {len(all_salaries)}")
        print(all_salaries)
        with open("../Data/mlb_salaries.json", "w") as f:
            f.write(json.dumps(all_salaries))
        return all_salaries

    @staticmethod
    def clean_spaces(text: str) -> str:
        """Removes multiple spaces between words in a string."""
        return " ".join(text.split())

    def parse_salaries(self, response: requests.Response):
        """ extracts salaries from response """
        soup = BeautifulSoup(response.content, 'html5lib')
        table = soup.find('table', attrs={'class': 'table dataTable premium'})
        if not table:
            raise Exception("table not found")

        # parse table head
        headers = []
        for th in table.find("thead").find_all('th'):
            th_text = self.clean_spaces(th.text.replace("\n", ""))
            headers.append(th_text)

        rows = []
        for row in table.find("tbody").find_all('tr'):
            cols = self.parse_table_columns(row)
            row_data = dict(zip(headers, cols))
            rows.append({row_data["Team"]: row_data})

        return rows

    def parse_table_columns(self, row):
        cols = []
        for td in row.find_all("td"):
            self.decompose_display_none(td)
            text = self.clean_spaces(td.text)
            cols.append(text)

        return cols

    @staticmethod
    def decompose_display_none(element):
        try:
            element.find('span', class_='d-none').decompose()
        except Exception:
            pass


if __name__ == "__main__":
    proxy = "" # "http://127.0.0.1:8080"
    headers = {}
    scraper = SpotracScraper(headers, proxy)

    scraper.get_salaries(2011, 2025)
