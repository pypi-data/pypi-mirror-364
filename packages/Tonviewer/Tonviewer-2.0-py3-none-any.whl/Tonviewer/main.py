import cloudscraper
from bs4 import BeautifulSoup

class Wallet:
    def __init__(self , wallet: str):
        self.scraper = cloudscraper.create_scraper()
        self.wallet: str = wallet
        self.response = self.scraper.get(f"https://tonviewer.com/{self.wallet}")
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def balance(self):
        try:
            if self.response.status_code == 200:
                ton = self.soup.find("div", class_="bdtytpm b1249k0b")
                usdt = self.soup.find("div", class_="bdtytpm b1ai646e")
                if ton and usdt:
                    print(ton.text.strip() ,usdt.text.strip())
            else:
                print("Failed to retrieve data.")
        except Exception as e :
            print(e)



