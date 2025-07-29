# FMScraper

A Selenium-powered Python tool for scraping football match data from [FotMob](https://www.fotmob.com/).

Inspired by: [Webscraper-PremData](https://github.com/deanpatel2/Webscraper-PremData/tree/main) and [scraping-football-sites](https://github.com/axelbol/scraping-football-sites/tree/main)

## Overview
FMScraper is a web scraping tool designed to extract comprehensive football match statistics and data from [FotMob](https://www.fotmob.com/), a popular platform for football statistics, live scores, and match analysis. The tool automates the data collection process, handling JavaScript-driven content and dynamic page layouts that traditional scraping methods cannot access.

## Features

- Scrapes match info from FotMob
- Handles JavaScript-driven layouts using Selenium
- Extracts data for specific leagues, seasons, and matchweeks

## Requirements

- Python 3.8+
- [Selenium](https://selenium.dev/)
- [beautifulsoup4 ](https://pypi.org/project/beautifulsoup4/)
- [requests](https://pypi.org/project/requests/)
- [chromedriver](https://chromedriver.chromium.org/) or another compatible WebDriver

## Disclaimer
For educational and research purposes only. Do not use it commercially.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MieszkoPugowski/FMScraper.git
cd FMScraper
```

2. Install using pip:
```bash
pip install fmscraper
```
## Example usage
```python
from fmscraper import MatchStats, MatchLinks
game_ids = MatchLinks(league_id=38,league="bundesliga",season='2024-2025').get_matches_ids(32)

some_game = game_ids[0]

data = MatchStats(some_game)

# List of all shots in a game
shotlist = data['content']['shotmap']['shots']
print(shotlist)
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue.


