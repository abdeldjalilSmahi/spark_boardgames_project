import ijson
from itertools import zip_longest
import json


def save_dict_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_properties(filename='./scrapped_data/bgg_data.json', output_path="./data"):
    artists_objectids = {}
    designers_objectids = {}
    subdomains_objectids = {}
    mechanisms_objectids = {}
    categories_objectids = {}
    families_objectids = {}
    companies_objectids = {}
    with open(filename, 'r', encoding='utf-8') as file:
        items = ijson.items(file, 'item')
        for item in items:
            boardgame_id = item['object_id']
            subdomains = item['subdomain']
            mechanisms = item['mechanism']
            families = item['family']
            categories = item['categories']
            companies = item['companies']
            artists = item['artists']
            designers = item['designers']
            for subdomain, mechanism, family, category, company, artist, designer \
                    in zip_longest(subdomains, mechanisms, families
                , categories, companies
                , artists, designers):

                if subdomain is not None:
                    subdomains_objectids.setdefault(subdomain, []).append(boardgame_id)

                if mechanism is not None:
                    mechanisms_objectids.setdefault(mechanism, []).append(boardgame_id)

                if family is not None:
                    families_objectids.setdefault(family, []).append(boardgame_id)

                if category is not None:
                    categories_objectids.setdefault(category, []).append(boardgame_id)

                if company is not None:
                    companies_objectids.setdefault(company, []).append(boardgame_id)

                if artist is not None:
                    artists_objectids.setdefault(artist, []).append(boardgame_id)

                if designer is not None:
                    designers_objectids.setdefault(designer, []).append(boardgame_id)

        save_dict_to_json(subdomains_objectids, f'{output_path}/subdomains_objectids.json')
        save_dict_to_json(mechanisms_objectids, f'{output_path}/mechanisms_objectids.json')
        save_dict_to_json(families_objectids, f'{output_path}/families_objectids.json')
        save_dict_to_json(categories_objectids, f'{output_path}/categories_objectids.json')
        save_dict_to_json(companies_objectids, f'{output_path}/companies_objectids.json')
        save_dict_to_json(artists_objectids, f'{output_path}/artists_objectids.json')
        save_dict_to_json(designers_objectids, f'{output_path}/designers_objectids.json')

if __name__ == '__main__':
    get_properties()
