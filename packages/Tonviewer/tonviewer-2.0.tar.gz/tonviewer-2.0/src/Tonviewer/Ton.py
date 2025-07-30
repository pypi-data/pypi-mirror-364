from bs4 import BeautifulSoup
from .main import Wallet

class Coin(Wallet):
    def __init__(self , coin: str):
        self.coin = coin
        self.url = "https://www.coingecko.com/en/coins/"
        super().__init__(wallet=coin)
        self.html = self.scraper.get(self.url + self.coin).text
        self.soup = BeautifulSoup(self.html, "html.parser")

    def price(self) -> str:
        try:
            price_div = self.soup.find("div",
                                  class_="tw-font-bold tw-text-gray-900 dark:tw-text-moon-50 tw-text-3xl md:tw-text-4xl tw-leading-10")
            if price_div:
                span = price_div.find("span", attrs={"data-converter-target": "price"})
                if span:
                    print(span.text.strip())

        except Exception as e:
            print(" Error fetching price:", e)
        return None

    def about(self):
        try:
            about_section = self.soup.find('div', class_="coin-page-editorial-content")
            if about_section:
                first_paragraph = about_section.find('p')
                if first_paragraph:
                    print(first_paragraph.text.strip())
                else:
                    print("❌ not found.")
            else:
                print("❌ About section not found.")
        except Exception as e:
            print("❌ Error extracting about text:", e)






