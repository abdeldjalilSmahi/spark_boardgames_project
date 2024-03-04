import os
import scrapy
from bs4 import BeautifulSoup
from scrapy_selenium import SeleniumRequest
from models.models import Category
import json
import xml.etree.ElementTree as ET
import re


class BoardgamecategorySpider(scrapy.Spider):
    name = "boardgamecategory"
    allowed_domains = ["boardgamegeek.com"]
    start_urls = ["https://boardgamegeek.com/boardgamecategory/"]

    def __init__(self, *args, **kwargs):
        super(BoardgamecategorySpider, self).__init__(*args, **kwargs)
        output_directory = './scrapped_data'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 60,  # Temps en secondes avant d'abandonner une requête
        'DOWNLOAD_DELAY': 5,  # Délai en secondes entre chaque requête
        'SCRAPEOPS_API_KEY': 'adb5f5fe-dcae-454e-b30a-711a1e28e4e8', # Ma clé pour reccuperer des fake useragents
        'SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT': 'https://headers.scrapeops.io/v1/user-agents',# j'envoie une request pour reccupérer des fake user agents
        'SCRAPEOPS_FAKE_USER_AGENT_ENABLED': True, # Ce paramètre pour activer l'utilisation des fake user agents
        'SCRAPEOPS_NUM_RESULTS': 1000, #nombre de fake user agents souhaité.
        'RETRY_TIMES': 2,  # Nombre maximal de tentatives de réessai
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
        'FEEDS': { # Format de stockage
            os.path.join('scrapped_data', 'bgg_category_data.json'): {
                'format': 'json',
                'encoding': 'utf-8',
                'ensure_ascii': False,
                'indent': 4,
                'overwrite': True
            },
        },
        'DOWNLOADER_MIDDLEWARES': { # Middlewares.
            'boardgames.middlewares.ScrapeOpsFakeUserAgentMiddleware': 400,
            'boardgames.middlewares.CustomRetryMiddleware': 550,
            'boardgames.middlewares.HeadlessChromeSeleniumMiddleware': 800
        },
        # Paramètres Selenium ajoutés
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': 'C:/chromedriver/chromedriver.exe', #path de chrome driver.
        'SELENIUM_DRIVER_ARGUMENTS': ['--headless', '--disable-gpu'] #desativer le lancement de la fenetre du chrome
    }

    def start_requests(self):
        filename = './data/categories_objectids.json'
        with open(filename, 'r', encoding='utf-8') as file:
            items = json.load(file)
        index = 0
        for key in items:
            index += 1
            url_request = f"{self.start_urls[0]}{key}"
            yield SeleniumRequest(url=url_request, callback=self.parse, meta={"id": key, 'boardgames': items[key]})
            if index == 10:
                break

    def parse(self, response):

        if response.status != 200 or 'retry_times' in response.meta:
            # Gérer les réponses après les réessais ou les rafraîchissements
            # Par exemple, enregistrer l'échec ou prendre une autre mesure corrective
            self.logger.error(f"Échec après réessais pour l'URL: {response.url}")
            return

        print(response.url)
        id = response.meta['id']
        boardgames = response.meta['boardgames']
        boardgamecateory = self.build_boardgamecategory(response, id, response.url, boardgames)
        yield boardgamecateory.dict()

    def extract_name(self, response):
        """
        Méthode qui permet de réccupérer le nom de la category.
        Fait le Nettoyage du titre de la page.
        """
        try:
            h1_element = response.xpath('//h1[a[@ui-sref="geekitem.overview"]]')
            if h1_element:
                title = h1_element.css('a[ui-sref="geekitem.overview"]::text').get()
                # Nettoyage : Nettoyer le titre pour enlever les espaces blancs et les tabulations
                title = title.strip() if title is not None else ''
                return title
            else:
                return ''
        except Exception as e:
            # Gestion des exceptions
            self.logger.error("Une erreur s'est produite lors du scraping du titre : %s", e)
            return ''

    def extract_description(self, response):
        """
        Méthode pour scrapper la description de la category du boardgame.
        """
        try:
            # Extraction du contenu HTML ciblé
            html_content = response.css('div[ng-bind-html="geekitemctrl.wikitext|to_trusted"]').get()

            # Vérification de la présence de contenu
            if not html_content:
                return ""

            # Utilisation de BeautifulSoup pour le parsing HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Suppression des balises indésirables et récupération du texte
            for tag in soup(['em', 'strong', 'a', 'br', 'span', 'i', 'u']):
                tag.decompose()

            # Obtention du texte nettoyé
            description_clean = soup.get_text(separator=' ', strip=True)

            # Remplacement des espaces blancs multiples par un seul espace
            description_clean = re.sub(r'\s+', ' ', description_clean)

            return description_clean

        except Exception as e:
            # Gestion des exceptions
            self.logger.error("Erreur lors du scraping de la description : %s", e)
            return ""

    def build_boardgamecategory(self, response, id, url, boardgames):
        name = self.extract_name(response)
        description = self.extract_description(response).strip()
        author = 22205250
        id = int(id)
        company = Category(author, id, url, name, description, boardgames)
        return company
