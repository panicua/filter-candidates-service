import scrapy
from scrapy.http import Response
from selenium import webdriver


# DON'T FORGET TO REMOVE COMMENTS
class WorkUaSpider(scrapy.Spider):
    name = "work-ua"
    allowed_domains = ["work.ua"]
    start_urls = ["https://work.ua"]

    def __init__(self) -> None:
        super().__init__()
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.implicitly_wait(10)

    def parse(self, response: Response, **kwargs) -> None:

        while True:
            break
