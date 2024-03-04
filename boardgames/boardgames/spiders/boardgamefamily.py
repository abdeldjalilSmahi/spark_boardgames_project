import json
import os
import re
import xml.etree.ElementTree as ET

import requests
import scrapy
from bs4 import BeautifulSoup
from models.models import Family


class BoardgamefamilySpider(scrapy.Spider):
    """
    Spider pour scraper boardgamefamily
    Utilisation de la version 2 de l'api de boardgamegeek https://api.geekdo.com/xmlapi2/family
    Utilisation de fakeUserAgent pour contouner le nombre limité de requetes.
    """
    name = "boardgamefamily"
    allowed_domains = ["api.geekdo.com"]
    start_urls = ["https://api.geekdo.com/xmlapi2/family"]

    def __init__(self, *args, **kwargs):
        super(BoardgamefamilySpider, self).__init__(*args, **kwargs)
        output_directory = './scrapped_data'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    custom_settings = {
        # Configuration des settings, notamment le fakeUserAgent.
        'SCRAPEOPS_API_KEY': 'adb5f5fe-dcae-454e-b30a-711a1e28e4e8',
        'SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT': 'https://headers.scrapeops.io/v1/user-agents',
        'SCRAPEOPS_FAKE_USER_AGENT_ENABLED': True,
        'SCRAPEOPS_NUM_RESULTS': 1000,
        'FEEDS': {
            os.path.join('scrapped_data', 'bgg_family_data.json'): {
                'format': 'json',
                'encoding': 'utf-8',
                'ensure_ascii': False,
                'indent': 4,
                'overwrite': True
            },
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Appel au middleware de fakeUserAgent et la priorité.
            'boardgames.middlewares.ScrapeOpsFakeUserAgentMiddleware': 400,
        },
    }

    def start_requests(self):
        filename = './data/families_objectids.json'
        with open(filename, 'r', encoding='utf-8') as file:
            items = json.load(file)

        for key in items:

            url = f'https://boardgamegeek.com/{self.name}/{key}'
            url_request = f"{self.start_urls[0]}?id={key}&type={self.name}"
            yield scrapy.Request(url=url_request, callback=self.parse,
                                 meta={'id': key, 'url': url, 'boardgames': items[key]})

    def parse(self, response):
        id = response.meta['id']
        url = response.meta['url']
        url_response = requests.get(url)
        final_url = url_response.url
        boardgames = response.meta['boardgames']
        root = ET.fromstring(response.body)
        boardgamepublisher = self.build_boardgamepublisher(root, id, final_url, boardgames)
        yield boardgamepublisher.dict()

    def extract_name(self, root):
        # Extraction du nom
        name_element = root.find(".//name[@type='primary']")
        name = name_element.get('value') if name_element is not None else ""

        return name

    def extract_description(self, root):
        description_element = root.find(".//description")
        if description_element is not None and description_element.text is not None:
            description_html = description_element.text
            soup = BeautifulSoup(description_html, 'html.parser')
            for tag in soup(['em', 'strong', 'a', 'br', 'span', 'i', 'u']):
                tag.decompose()
            description_clean = soup.get_text()

            # Remplacer les espaces blancs multiples par un seul espace
            description_clean = re.sub(r'\s+', ' ', description_clean)

            # Supprimer les espaces en début et fin de chaîne
            description_clean = description_clean.strip()
        else:
            description_clean = ""

        return description_clean

    def build_boardgamepublisher(self, root, id, url, boardgames):
        name = self.extract_name(root)
        description = self.extract_description(root).strip()
        author = 22205250
        id = int(id)
        company = Family(author, id, url, name, description, boardgames)
        return company
