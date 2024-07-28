from typing import Union

import scrapy
from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from scrapy import Item, Field


class UrlItem(Item):
    url = Field()


# DON'T FORGET TO REMOVE COMMENTS
class WorkUaSpider(scrapy.Spider):
    name = "work-ua"
    allowed_domains = ["work.ua"]
    start_urls = ["https://work.ua"]
    employer_url = "https://www.work.ua/employer/"

    def __init__(self) -> None:
        super().__init__()
        # position will be set with telegram bot, later
        self.position = "Python developer"
        self.location = "Вся Україна"
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.implicitly_wait(10)

    def parse(self, response: Response, **kwargs) -> None:
        self.open_employer_page()
        self.find_candidates_by_position(self.position, self.location)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/resumes/']")
            )
        )

        # Extract candidate URLs
        candidates_links = self.driver.find_elements(
            By.CSS_SELECTOR, "div.col-md-8 h2.mt-0 a"
        )
        for link in candidates_links:
            url = link.get_attribute("href")
            print(f"UUURL {url}")
            yield UrlItem(url=url)

        # time.sleep(5)

    def find_candidates_by_position(
        self, position: str, location: str
    ) -> None:
        position_field = self.driver.find_element(
            By.CSS_SELECTOR, "input[placeholder='Посада']"
        )
        position_field.send_keys(position)
        location_field = self.driver.find_element(
            By.CSS_SELECTOR, "input[placeholder='Місто']"
        )
        location_field.send_keys(location)

        search_button = self.driver.find_element(
            By.CSS_SELECTOR, "button[type='submit']"
        )
        search_button.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/resumes/']")
            )
        )

    def open_employer_page(self) -> None:
        self.driver.get(self.employer_url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/employer/']")
            )
        )

    def close(self, reason) -> None:
        self.driver.quit()


if __name__ == "__main__":
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(WorkUaSpider)
    process.start()
