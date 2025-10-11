import logging
from typing import Type, Literal
import time

from intern_bot_core.data_scraper import BaseScraper
from intern_bot.data_scraper.scrapers import NokiaScraper
from intern_bot.data_scraper.scrapers import PWRScraper
from intern_bot.data_scraper.scrapers import SiiScraper

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class DataScraper:
    _scrappers: dict[str] = {'PWR': PWRScraper, 'Nokia': NokiaScraper, 'Sii': SiiScraper}

    @classmethod
    def _get_scraper(cls, source: str) -> Type[BaseScraper]:
        if source not in cls._scrappers:
            raise ValueError(f'Wrong source provided: {source}')
        return cls._scrappers[source]

    @classmethod
    def scrape_offers(
        cls, scraper_name: Literal['PWR', 'Nokia', 'Sii']
    ) -> list[str]:
        scraper = cls._get_scraper(scraper_name)
        return scraper.scrape_offers()
    
    @classmethod
    def scrape_offer_details(cls, scraper_name: Literal['PWR', 'Nokia', 'Sii'], offer: str
                              ) -> dict[str, str]:
        scraper = cls._get_scraper(scraper_name)
        logging.info(f"Scraping details for: {offer}")
        try:
            detailed_offer = scraper.scrape_offer_details(offer)
            logging.info(f"Succesfully scraped offer details: {offer}")
        except Exception as e:
            logging.warning(f"Error fetching details for {scraper_name} job: {offer}: {e}")
        return detailed_offer
    
    @classmethod
    def scrape_offers_details(cls, scraper_name: Literal['PWR', 'Nokia', 'Sii'], offers: list[str]
                              ) -> list[dict[str, str]]:
        detailed_offers = []
        for offer in offers:
            if detailed_offer := cls.scrape_offer_details(scraper_name, offer):
                detailed_offers.append(detailed_offer)
            time.sleep(0.5)
            
        logging.info(f"Finished scraping {scraper_name}. Total offers with details: {len(detailed_offers)}")
        return detailed_offers
    


