import os
import scrapy
from bs4 import BeautifulSoup
from scrapy_selenium import SeleniumRequest
from models.models import Category, Subdomain
import json
import xml.etree.ElementTree as ET
import re


class BoardgamesubdomainSpider(scrapy.Spider):
    name = "boardgamesubdomain"
    allowed_domains = ["boardgamegeek.com"]
    start_urls = ["https://boardgamegeek.com/boardgamesubdomain/"]

    def __init__(self, *args, **kwargs):
        super(BoardgamesubdomainSpider, self).__init__(*args, **kwargs)
        output_directory = './scrapped_data'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 60,  # Temps en secondes avant d'abandonner une requête
        'DOWNLOAD_DELAY': 5,  # Délai en secondes entre chaque requête
        'RETRY_TIMES': 2,  # Nombre maximal de tentatives de réessai
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
        'FEEDS': {
            os.path.join('scrapped_data', 'bgg_subdomain_data.json'): {
                'format': 'json',
                'encoding': 'utf-8',
                'ensure_ascii': False,
                'indent': 4,
                'overwrite': True
            },
        },
        'DOWNLOADER_MIDDLEWARES': {
            'boardgames.middlewares.CustomRetryMiddleware': 550,
            'boardgames.middlewares.HeadlessChromeSeleniumMiddleware': 800
        },
        # Paramètres Selenium ajoutés
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': 'C:/chromedriver/chromedriver.exe',
        'SELENIUM_DRIVER_ARGUMENTS': ['--headless', '--disable-gpu']
    }

    def start_requests(self):
        filename = './data/subdomains_objectids.json'
        with open(filename, 'r', encoding='utf-8') as file:
            items = json.load(file)

        for key in items:

            url_request = f"{self.start_urls[0]}{key}"
            yield SeleniumRequest(url=url_request, callback=self.parse, meta={"id": key, 'boardgames': items[key]})


    def parse(self, response):

        if response.status != 200 or 'retry_times' in response.meta:
            # Gérer les réponses après les réessais ou les rafraîchissements
            # Par exemple, enregistrer l'échec ou prendre une autre mesure corrective
            self.logger.error(f"Échec après réessais pour l'URL: {response.url}")
            return

        id = response.meta['id']
        boardgames = response.meta['boardgames']
        boardgamecateory = self.build_boardgamepublisher(response, id, response.url, boardgames)
        yield boardgamecateory.dict()

    def extract_name(self, response):
        """
        Fonction indépendante pour scraper et nettoyer le nom de la page.
        """
        try:
            # Sélection de l'élément div avec la classe 'geekitem_name'
            name_div = response.css('div.geekitem_name::text').get()

            # Nettoyer le nom pour enlever les espaces blancs et les tabulations
            name = name_div.strip() if name_div is not None else ''

            return name
        except Exception as e:
            # Gérer les exceptions et afficher un message d'erreur
            self.logger.error("Une erreur s'est produite lors du scraping du nom : %s", e)
            return ''

    def scrap_description(self, response):
        """
        Fonction indépendante pour scraper la description de la page.
        """
        try:
            # Utiliser Scrapy pour obtenir le HTML brut
            html_content = response.css('div[ng-bind-html="geekitemctrl.wikitext|to_trusted"]').get()

            # Utiliser BeautifulSoup pour traiter le code HTML
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                paragraphs = soup.find_all('p')
                description = ' '.join(
                    [''.join(
                        [str(child) if child.name not in ['em', 'strong', 'a', 'br', 'span', 'i', 'u'] else child.text
                         for \
                         child in p.contents]) for
                        p in paragraphs])

                description_clean = soup.get_text()
                # Remplacer les espaces blancs multiples par un seul espace
                description_clean = re.sub(r'\s+', ' ', description_clean)

                # Supprimer les espaces en début et fin de chaîne
                description_clean = description_clean.strip()

                return description_clean
            else:
                return ""
        except Exception as e:
            # Gérer les exceptions
            self.logger.error("Une erreur s'est produite lors du scraping de la description : %s", e)
            return ""

    def extract_description(self, response):
        """
        Fonction pour scraper et nettoyer la description d'une page.
        """
        try:
            # Extraction du contenu HTML ciblé
            html_content = response.css('div.wiki').get()

            # Vérification de la présence de contenu
            if not html_content:
                return ""

            # Utilisation de BeautifulSoup pour le parsing HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Suppression des balises indésirables
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

    def build_boardgamepublisher(self, response, id, url, boardgames):
        name = self.extract_name(response)
        description = self.extract_description(response).strip()
        author = 22205250
        id = int(id)
        company = Subdomain(author, id, url, name, description, boardgames)
        return company
