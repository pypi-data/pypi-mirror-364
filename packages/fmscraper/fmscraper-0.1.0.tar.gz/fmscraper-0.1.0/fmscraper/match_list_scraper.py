"""

Author: Mieszko Pugowski

FotMob scraper

**FOR EDUCATIONAL PURPOSES ONLY**
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time


LEAGUE_ID = 38
LEAGUE = "bundesliga"
SEASON = "2024-2025"


class MatchLinks:
    def __init__(self, league_id:int,league:str, season:str):
        self.base_url = "https://www.fotmob.com/leagues"
        self.league_id = str(league_id)
        self.league = league
        self.season = season
        self.final_url = ""
        # Setting up selenium driver
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self._url_to_scrape()

    def _url_to_scrape(self):
        try:
            matches_url = "/".join([self.base_url, self.league_id,
                                    'matches',self.league])
            url_to_scrape = "?".join([matches_url, f"season={self.season}"])
            self.final_url = url_to_scrape
        except:
            return f"Please pick correct league's id or season (in format 20xx-20xx)"

    def _consent_fotmob(self):
        wait = WebDriverWait(self.driver, 5)
        consent_button = wait.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, "button.fc-button.fc-cta-consent.fc-primary-button"))
        )
        consent_button.click()


    def get_matches_ids(self,rounds):
        games_list = []
        games_ids = []
        self.driver.get(self.final_url)
        self._consent_fotmob()
        for i in range(rounds):
            round_i = self.final_url +f"&group=by-round&round={i}"
            self.driver.get(round_i)
            try:
                time.sleep(2)
                hrefs = [a.get_attribute("href") for a in
                         self.driver.find_elements(By.CSS_SELECTOR,
                                              "a.css-1ajdexg-MatchWrapper.e1mxmq6p0")]
                if not hrefs:
                    return "You have exceeded the number of rounds in the league"
                else:
                    games_list.extend(hrefs)
            except:
                print(f"Error: stale element reference for match {i}")
        self.driver.quit()
        for game in games_list:
            match_id = game.split('#')[-1]
            games_ids.append(match_id.replace("\n", ""))
        return games_ids


    def write_to_file(self,file_name,ids):
        with open(f"{file_name}.txt","w") as file:
            for id in ids:
                file.write(f'{id}\n')

