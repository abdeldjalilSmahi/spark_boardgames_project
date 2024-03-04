# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class BoardgamesSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class BoardgamesDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from scrapy_selenium import SeleniumMiddleware
from scrapy.http import HtmlResponse
from selenium.common.exceptions import TimeoutException


class HeadlessChromeSeleniumMiddleware(SeleniumMiddleware):
    """
    Class pour gérer orchestrer selenium avec scrapy.
    """
    def __init__(self, *args, **kwargs):
        self.request_count = 0
        self.max_requests = 1000  # Nombre maximal de requêtes avant de redémarrer le navigateur,
        # On fait comme ça car cumuler les fenetres chrome consome de la ram.
        self.initialize_browser()

    def initialize_browser(self):
        print("Initializing chrome driver...")
        # Configuration initiale du navigateur
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_service = Service('C:/chromedriver/chromedriver.exe')
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(60)

    def process_request(self, request, spider):
        self.request_count += 1
        if self.request_count > self.max_requests:
            self.restart_browser()

        try:
            self.driver.get(request.url)
            # Ici, vous pouvez ajouter d'autres interactions avec la page si nécessaire

            # Création de la réponse Scrapy
            return HtmlResponse(self.driver.current_url,
                                body=self.driver.page_source,
                                encoding='utf-8',
                                request=request)
        except TimeoutException:
            spider.logger.error(f"Timeout lors du chargement de la page: {request.url}")
            return HtmlResponse(request.url, status=500, request=request)

    def restart_browser(self):
        self.driver.quit()  # Fermer l'instance actuelle du navigateur
        self.initialize_browser()  # Initialiser une nouvelle instance du navigateur
        self.request_count = 0  # Réinitialiser le compteur de requêtes


from urllib.parse import urlencode
from random import randint
import requests


class ScrapeOpsFakeUserAgentMiddleware:
    """
    Class pour gérer le middleware de fake user agents
    """
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.scrapeops_api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = settings.get('SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT',
                                               'http://headers.scrapeops.io/v1/user-agents?')
        self.scrapeops_fake_user_agents_active = settings.get('SCRAPEOPS_FAKE_USER_AGENT_ENABLED', False)
        self.scrapeops_num_results = settings.get('SCRAPEOPS_NUM_RESULTS')
        self.headers_list = []
        self._get_user_agents_list()
        self._scrapeops_fake_user_agents_enabled()

    def _get_user_agents_list(self):
        payload = {'api_key': self.scrapeops_api_key}
        if self.scrapeops_num_results is not None:
            payload['num_results'] = self.scrapeops_num_results
        response = requests.get(self.scrapeops_endpoint, params=urlencode(payload))
        json_response = response.json()
        self.user_agents_list = json_response.get('result', [])

    def _get_random_user_agent(self):
        random_index = randint(0, len(self.user_agents_list) - 1)
        return self.user_agents_list[random_index]

    def _scrapeops_fake_user_agents_enabled(self):
        if self.scrapeops_api_key is None or self.scrapeops_api_key == '' or self.scrapeops_fake_user_agents_active == False:
            self.scrapeops_fake_user_agents_active = False
        else:
            self.scrapeops_fake_user_agents_active = True

    def process_request(self, request, spider):
        random_user_agent = self._get_random_user_agent()
        request.headers['User-Agent'] = random_user_agent

        print("********************************* NEW HEADER ARACHE *****************************")
        print(request.headers['User-Agent'])


from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from selenium.common.exceptions import TimeoutException


class CustomRetryMiddleware(RetryMiddleware):
    def process_exception(self, request, exception, spider):
        if isinstance(exception, TimeoutException):
            return self._retry(request, exception, spider)
