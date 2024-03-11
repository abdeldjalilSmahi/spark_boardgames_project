import os
import re
import sys
import scrapy
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from zip_csv.csv_parser import CSVParser
from models.models import Boardgame
from zip_csv.zip_downloader import ZipDownloader


class BoardgameSpider(scrapy.Spider):
    name = "boardgame"
    allowed_domains = ["api.geekdo.com"]
    start_urls = ["https://api.geekdo.com/xmlapi/"]

    def __init__(self, *args, **kwargs):
        """
        Initialise le spider, si le repertoire scrapped_data n'exsiste pars elle le crée.
        Vous trouvez aussi le settings personalisé de ce spider, comme le format du output.
        """
        super(BoardgameSpider, self).__init__(*args, **kwargs)
        output_directory = './scrapped_data'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    custom_settings = {
        'FEEDS': {
            os.path.join('scrapped_data', 'bgg_data.json'): {
                'format': 'json',
                'encoding': 'utf-8',
                'ensure_ascii': False,
                'indent': 4,
                'overwrite': True
            },
        },
    }

    def start_requests(self):
        """
        Ici Je lis le fichier telechargé du site boardgame que je le mets dans le répertoire data !
        EN CAS D'utilisation anterieur je vous prie de bien vouloir telehargé et unzippé le fichier zip de boardgameranks
        et le bien mettre dans le repertoire data en respectant le nom de fichier ci-dessous
        """
        print("Welcome to our boardgame scrapper")
        print("*************************************************************")
        csv_parser = CSVParser('./data/boardgames_ranks.csv')
        print("Debut de scrapping, ENJOY :D ")
        print("*************************************************************")
        for bgg_id in csv_parser.get_info():
            url_request = self.start_urls[0] + "boardgame" + "/" + bgg_id + "?stats=1"
            yield scrapy.Request(url=url_request, callback=self.parse,
                                 meta={'id': bgg_id})


    def parse(self, response):
        """
        Cette fonction parse chaque page et reccuprère les données tout en construisant l'objet boardgame qui sera
        serialisé par la suite.
        """
        bgg_id = response.meta['id']
        url = f"https://boardgamegeek.com/boardgame/{bgg_id}"
        root = ET.fromstring(response.body)
        boardgame = self.build_boardgame_from_api(root, bgg_id, url)
        yield boardgame.dict()

    def extract_name(self, root):
        """
        Cette fonction sert à Trouver l'élément 'name' avec l'attribut 'primary' à 'true' et obtenir son contenu textuel
        """

        primary_name_element = root.find(".//name[@primary='true']")
        primary_name = primary_name_element.text if primary_name_element is not None else ""

        return primary_name

    def extract_year_published(self, root):
        """
        Methode qui permet d'extraire l'année de publication du boardgame.
        Dans le cas ou il ne trouve pas l'année, ça retourne une chaine vide.
        """
        year_published_element = root.find(".//yearpublished")
        year_published = int(year_published_element.text) if year_published_element is not None else ""

        return year_published

    def extract_min_players(self, root):
        """
        Cette méthode extrait le nombre minimum des joueurs.
        """
        min_players_element = root.find(".//minplayers")
        min_players = int(min_players_element.text) if min_players_element is not None else 0
        return min_players

    def extract_max_players(self, root):
        """
        Cette fonction extrait le nombre maximum des joueurs.
        """
        max_players_element = root.find(".//maxplayers")
        max_players = int(max_players_element.text) if max_players_element is not None else self.extract_min_players(id)

        return max_players

    def extract_playing_time(self, root):
        """
        Cette fonction extrait la durée moyenne qui prend le jeu.
        """
        playing_time_element = root.find(".//playingtime")
        playing_time = int(playing_time_element.text) if playing_time_element is not None else 0
        return playing_time

    def extract_min_playing_time(self, root):
        """
       Cette fonction extrait la durée minimum qui prend le jeu.
        """
        min_playing_time_element = root.find(".//minplaytime")
        min_playing_time = int(min_playing_time_element.text) if min_playing_time_element is not None else 0
        return min_playing_time

    def extract_max_playing_time(self, root):
        """
               Cette fonction extrait la durée maximum qui prend le jeu.
               en cas d'echoue elle retourne le temps minimale.
        """
        max_playing_time_element = root.find(".//maxplaytime")
        max_playing_time = int(
            max_playing_time_element.text) if max_playing_time_element is not None else self.extract_min_playing_time()
        return max_playing_time

    def extract_recommended_age(self, root):
        """
        Fonction qui extrait l'age recommandé du jeu.
        Retourne 0 en cas d'échoue d'extraction.
        """
        age_element = root.find(".//age")
        recommended_age = int(age_element.text) if age_element is not None else 0
        return recommended_age

    def extract_description(self, root):
        """
        Extrait la description du boardgame.
        Nettoie la description de tout type de balise qui peut exister en utilisant BS4.
        En cas d'échoue elle retourne une chaine de caractère vide.
        """
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

    def extract_geek_rating(self, root):
        """
        Cette fonction extrait le geek rating du jeu 'bayes average' en deux chiffres après la virgule.
        """
        bayesaverage_element = root.find(".//bayesaverage")
        if bayesaverage_element is not None and 'value' in bayesaverage_element.attrib:
            geek_rating = round(float(bayesaverage_element.attrib['value']), 2)
        else:
            geek_rating = 0.0
        return geek_rating

    def extract_avg_rating(self, root):
        """
        Cette fonction extrait la moyenne de rating.
        """
        average_element = root.find(".//average")
        if average_element is not None and 'value' in average_element.attrib:
            avg_rating = round(float(average_element.attrib['value']), 2)
        else:
            avg_rating = 0.0
        return avg_rating

    def extract_rank(self, root):
        """
        Cette méthode extrait le rank du boardgame, si le jeu il non ranké  je retourne le nombre maximal des entiers.
        """
        rank_element = root.find(".//rank[@friendlyname='Board Game Rank']")
        if rank_element is not None:
            rank_value = rank_element.attrib['value']
            rank = int(rank_value) if rank_value != "Not Ranked" else sys.maxsize
        else:
            rank = sys.maxsize

        return rank

    def extract_num_voters(self, root):
        """
        Méthode qui extrait le nombre de voters.
        """
        usersrated_element = root.find(".//usersrated")
        if usersrated_element is not None and 'value' in usersrated_element.attrib:
            num_voters = int(usersrated_element.attrib['value'])
        else:
            num_voters = 0
        return num_voters

    def extract_subdomain_ids(self, root):
        """
        Méthode qui extrait la liste des ids de subdomains.
        """
        subdomain_elements = root.findall(".//boardgamesubdomain")
        subdomain_ids = [int(element.attrib['objectid']) for element in subdomain_elements if
                         'objectid' in element.attrib]
        return subdomain_ids

    def extract_mechanic_ids(self, root):
        """
        Cette méthode extrait la liste des ids de mechanics.
        """
        mechanic_elements = root.findall(".//boardgamemechanic")
        mechanic_ids = [int(element.attrib['objectid']) for element in mechanic_elements if
                        'objectid' in element.attrib]
        return mechanic_ids

    def extract_family_ids(self, root):
        """
        Méthode qui extrait la liste des ids des familles de boardgame.
        """
        family_elements = root.findall(".//boardgamefamily")
        family_ids = [int(element.attrib['objectid']) for element in family_elements if 'objectid' in element.attrib]
        return family_ids

    def extract_category_ids(self, root):
        """
         Méthode qui extrait la liste des ids des categories de boardgame.
       """
        category_elements = root.findall(".//boardgamecategory")
        category_ids = [int(element.attrib['objectid']) for element in category_elements if
                        'objectid' in element.attrib]
        return category_ids

    def extract_publisher_ids(self, root):
        """
         Méthode qui extrait la liste des ids des publishers de boardgame.
       """
        category_elements = root.findall(".//boardgamepublisher")
        category_ids = [int(element.attrib['objectid']) for element in category_elements if
                        'objectid' in element.attrib]
        return category_ids

    def extract_artist_ids(self, root):
        """
         Méthode qui extrait la liste des ids des artists de boardgame.
        """
        category_elements = root.findall(".//boardgameartist")
        category_ids = [int(element.attrib['objectid']) for element in category_elements if
                        'objectid' in element.attrib]
        return category_ids

    def extract_designer_ids(self, root):
        """
         Méthode qui extrait la liste des ids des designers de boardgame.
        """
        category_elements = root.findall(".//boardgamedesigner")
        category_ids = [int(element.attrib['objectid']) for element in category_elements if
                        'objectid' in element.attrib]
        return category_ids

    def extract_boardgames_reimplemented_ids(self, root):
        """
         Méthode qui extrait la liste des ids des boardgames reimplemented.
        """
        category_elements = root.findall(".//boardgameimplementation")
        category_ids = [int(element.attrib['objectid']) for element in category_elements if
                        'objectid' in element.attrib]
        return category_ids

    def build_boardgame_from_api(self, root, id, url):
        """
        Cette méthode fait appelle à toutes les méthodes precedement decrites et construit l'objet boardgame
        et le retourne.
        """
        name = self.extract_name(root)
        year = self.extract_year_published(root)
        min_player = self.extract_min_players(root)
        max_player = self.extract_max_players(root)
        playing_time = self.extract_playing_time(root)
        min_playing_time = self.extract_min_playing_time(root)
        max_playing_time = self.extract_max_playing_time(root)
        age = self.extract_recommended_age(root)
        description = self.extract_description(root)
        geek_rating = self.extract_geek_rating(root)
        avg_rating = self.extract_avg_rating(root)
        rank = self.extract_rank(root)
        num_voters = self.extract_num_voters(root)
        subdomains = self.extract_subdomain_ids(root)
        mechanics = self.extract_mechanic_ids(root)
        families = self.extract_family_ids(root)
        categories = self.extract_category_ids(root)
        publishers = self.extract_publisher_ids(root)
        artists = self.extract_artist_ids(root)
        designers = self.extract_designer_ids(root)
        boardgames_reimplemented = self.extract_boardgames_reimplemented_ids(root)
        author = 22205250
        bgg = Boardgame(author, int(id), url, name, year, min_player, max_player, playing_time, min_playing_time,
                        max_playing_time, age, geek_rating, avg_rating, num_voters, rank, description, subdomains,
                        mechanics, families, categories, publishers, artists, designers, boardgames_reimplemented)

        return bgg
