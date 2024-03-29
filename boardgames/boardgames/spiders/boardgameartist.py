import json
import os
import re
import xml.etree.ElementTree as ET

import requests
import scrapy
from bs4 import BeautifulSoup
from models.models import Artist

class BoardgameartistSpider(scrapy.Spider):
    name = "boardgameartist"
    allowed_domains = ["api.geekdo.com"]
    start_urls = ["https://api.geekdo.com/xmlapi/"]

    def __init__(self, *args, **kwargs):
        super(BoardgameartistSpider, self).__init__(*args, **kwargs)
        output_directory = './scrapped_data'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    custom_settings = {
        'FEEDS': {
            os.path.join('scrapped_data', 'bgg_artist_data.json'): {
                'format': 'json',
                'encoding': 'utf-8',
                'ensure_ascii': False,
                'indent': 4,
                'overwrite': True
            },
        },
    }

    def start_requests(self):
        filename = './data/artists_objectids.json'
        with open(filename, 'r', encoding='utf-8') as file:
            items = json.load(file)

        for key in items:

            url = f'https://boardgamegeek.com/{self.name}/{key}'
            url_request = self.start_urls[0] + self.name + "/" + key
            yield scrapy.Request(url=url_request, callback=self.parse,
                                 meta={'id': key, 'url': url, 'boardgames': items[key]})

    def parse(self, response):
        id = response.meta['id']
        url = response.meta['url']
        boardgames = response.meta['boardgames']
        root = ET.fromstring(response.body)
        boardgamepublisher = self.build_boardgamepublisher(root, id, url, boardgames)
        yield boardgamepublisher.dict()

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
        company = Artist(author, id, url, name, description, boardgames)
        return company
