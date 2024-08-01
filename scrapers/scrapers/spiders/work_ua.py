import time

import scrapy
from scrapy import Item, Field
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from constants import LOCATION, EXPERIENCE, SALARY


class UrlItem(Item):
    url = Field()


# DON'T FORGET TO REMOVE COMMENTS
class WorkUaSpider(scrapy.Spider):
    name = "work-ua"
    allowed_domains = ["work.ua"]
    start_urls = ["https://work.ua"]
    employer_url = "https://www.work.ua/employer/"
    resumes_url = "https://www.work.ua/resumes"

    def __init__(self) -> None:
        super().__init__()
        self.job_position = "Python developer".lower().strip()
        self.location = LOCATION["Вся Україна"]
        self.experience = [EXPERIENCE["Від 1 до 2 років"], EXPERIENCE["До 1 року"]]
        self.salary = SALARY["до 30 000 грн"]
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.implicitly_wait(10)

    def parse(self, response: Response, **kwargs) -> None:
        self.open_employer_page()
        self.find_candidates_by_filters()

        # Extract candidate URLs
        candidates_links = self.driver.find_elements(
            By.CSS_SELECTOR, "div.col-md-8 h2.mt-0 a"
        )
        for link in candidates_links:
            url = link.get_attribute("href")
            print(f"UUURL {url}")
            yield UrlItem(url=url)

        time.sleep(5)

    def find_candidates_by_filters(self) -> None:
        search_field = self.start_urls[0] + "/"
        if self.location is not None:
            search_field += f"resumes-{self.location}-"
        else:
            search_field += f"resumes-"
        if self.job_position is not None:
            transformed_job_position = "+".join(self.job_position.split())
            search_field += f"{transformed_job_position}/?"
        else:
            raise Exception("Position is not set")

        candidate_filter = []
        if self.experience is not None:
            transformed_experience = "+".join([str(x) for x in self.experience])
            candidate_filter.append(f"experience={transformed_experience}")

        if self.salary is not None:
            candidate_filter.append(f"salaryto={SALARY['до 30 000 грн']}")
        if candidate_filter:
            search_field += "&".join(candidate_filter)

        self.driver.get(search_field)

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
