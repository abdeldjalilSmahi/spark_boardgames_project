from datetime import datetime
from typing import Optional


class Entity:
    def __init__(self, author: int, object_id, url, name, description):
        self.created_at = datetime.now()
        self.object_id = object_id
        self.url = url
        self.name = name
        self.description = description
        self.created_by = author
        self.updated_at: Optional[datetime] = None
        self.updated_by: Optional[int] = None


class Boardgame(Entity):
    def __init__(self, author: int, object_id, url, name, published_year, min_player,
                 max_player, playing_time, playing_min_time, playing_max_time,
                 age, geek_rating, avg_rating, num_voters, rank, description,
                 subdomain=None, mechanism=None, family=None, categories=None,
                 companies=None, artists=None, designers=None, boardgames_reimplemented=None):
        super().__init__(author, object_id, url, name, description)
        self.published_year = published_year
        self.min_player = min_player
        self.max_player = max_player
        self.playing_time = playing_time
        self.playing_min_time = playing_min_time
        self.playing_max_time = playing_max_time
        self.age = age
        self.rank = rank
        self.geek_rating = geek_rating
        self.avg_rating = avg_rating
        self.num_voters = num_voters
        self.boardgame_reimplemented = list(
            set(boardgames_reimplemented)) if boardgames_reimplemented is not None else []
        self.subdomain = list(set(subdomain)) if subdomain is not None else []
        self.mechanism = list(set(mechanism)) if mechanism is not None else []
        self.family = list(set(family)) if family is not None else []
        self.categories = list(set(categories)) if categories is not None else []
        self.companies = list(set(companies)) if companies is not None else []
        self.artists = list(set(artists)) if artists is not None else []
        self.designers = list(set(designers)) if designers is not None else []

    def dict(self):
        d = super().__dict__.copy()  # Créer une copie du dictionnaire
        d['created_at'] = d['created_at'].isoformat() if d['created_at'] else None
        return d


class Subdomain(Entity):

    def __init__(self, author: int, object_id, url, name, description, boardgames=None):
        super().__init__(author, object_id, url, name, description)
        self.boardgames = boardgames

    def dict(self):
        d = super().__dict__.copy()  # Créer une copie du dictionnaire
        d['created_at'] = d['created_at'].isoformat() if d['created_at'] else None
        return d


class Mechanism(Entity):

    def __init__(self, author: int, object_id, url, name, description, boardgames=None):
        super().__init__(author, object_id, url, name, description)
        self.boardgames = boardgames

    def dict(self):
        d = super().__dict__.copy()  # Créer une copie du dictionnaire
        d['created_at'] = d['created_at'].isoformat() if d['created_at'] else None
        return d


class Family(Entity):

    def __init__(self, author: int, object_id, url, name, description, boardgames=None):
        super().__init__(author, object_id, url, name, description)
        self.boardgames = boardgames

    def dict(self):
        d = super().__dict__.copy()  # Créer une copie du dictionnaire
        d['created_at'] = d['created_at'].isoformat() if d['created_at'] else None
        return d


class Category(Entity):
    # sera scrapé

    def __init__(self, author: int, object_id, url, name, description, boardgames=None):
        super().__init__(author, object_id, url, name, description)
        self.boardgames = boardgames

    def dict(self):
        d = super().__dict__.copy()  # Créer une copie du dictionnaire
        d['created_at'] = d['created_at'].isoformat() if d['created_at'] else None
        return d


class Company(Entity):

    def __init__(self, author: int, object_id, url, name, description, boardgames=None):
        super().__init__(author, object_id, url, name, description)
        self.boardgames = boardgames

    def dict(self):
        d = super().__dict__.copy()  # Créer une copie du dictionnaire
        d['created_at'] = d['created_at'].isoformat() if d['created_at'] else None
        return d


class Artist(Entity):

    def __init__(self, author: int, object_id, url, name, description, boardgames=None):
        super().__init__(author, object_id, url, name, description)
        self.boardgames = boardgames

    def dict(self):
        d = super().__dict__.copy()  # Créer une copie du dictionnaire
        d['created_at'] = d['created_at'].isoformat() if d['created_at'] else None
        return d


class Designer(Entity):

    def __init__(self, author: int, object_id, url, name, description, boardgames=None):
        super().__init__(author, object_id, url, name, description)
        self.boardgames = boardgames

    def dict(self):
        d = super().__dict__.copy()  # Créer une copie du dictionnaire
        d['created_at'] = d['created_at'].isoformat() if d['created_at'] else None
        return d
