import json
import os
import re
import xml.etree.ElementTree as ET

import requests
import scrapy
from bs4 import BeautifulSoup
from models.models import Company

class BoardgamepublisherSpider(scrapy.Spider):
    name = "boardgamepublisher"
    allowed_domains = ["api.geekdo.com"]
    start_urls = ["https://api.geekdo.com/xmlapi/"]

    def __init__(self, *args, **kwargs):
        super(BoardgamepublisherSpider, self).__init__(*args, **kwargs)
        output_directory = './scrapped_data'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    custom_settings = {
        'FEEDS': {
            os.path.join('scrapped_data', 'bgg_publisher_data.json'): {
                'format': 'json',
                'encoding': 'utf-8',
                'ensure_ascii': False,
                'indent': 4,
                'overwrite': True
            },
        },
    }

    def start_requests(self):
        filename = './data/companies_objectids.json'
        with open(filename, 'r', encoding='utf-8') as file:
            items = json.load(file)
        index = 0
        for key in items:
            index += 1
            url = f'https://boardgamegeek.com/{self.name}/{key}'
            url_request = self.start_urls[0] + self.name + "/" + key
            yield scrapy.Request(url=url_request, callback=self.parse,
                                 meta={'id': key, 'url': url, 'boardgames': items[key]})
            if index == 10:
                break

    def parse(self, response):
        id = response.meta['id']
        url = response.meta['url']
        url_response = requests.get(url)
        final_url = url_response.url
        boardgames = response.meta['boardgames']
        root = ET.fromstring(response.body)
        boardgame_publisher = self.build_boardgamepublisher(root, id, final_url, boardgames)
        yield boardgame_publisher.dict()

    def extract_name(self, root):
        primary_name_element = root.find(".//name")
        primary_name = primary_name_element.text if primary_name_element is not None else ""

        return primary_name

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
        company = Company(author, id, url, name, description, boardgames)
        return company
