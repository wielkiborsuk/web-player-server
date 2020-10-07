'''bookmark manager functionality for podcasts and audiobooks'''
import json
from collections import namedtuple
from tinydb import TinyDB, where
from flask import Blueprint, request

mod = Blueprint('bookmark_handler', __name__, url_prefix='/bookmark')

Bookmark = namedtuple('Bookmark', ['id', 'file', 'time'])


class BookmarkRepo:
    '''repository used to manage bookmark objects in a database'''
    def __init__(self, dbfile):
        '''create repository using a specific database file'''
        self.dataase = TinyDB(dbfile)

    def put(self, bookmark:Bookmark):
        '''put new or update a bookmark'''
        self.dataase.upsert(bookmark._asdict(), where('id') == bookmark.id)

    def get(self, book_id) -> Bookmark:
        '''get a bookmark by book id'''
        result = self.dataase.search(where('id') == book_id)
        return Bookmark(**result[0]) if result else None

    def list(self) -> Bookmark:
        '''return all bookmarks, for debugging purposes'''
        return [Bookmark(**row) for row in self.dataase.all()]


def _get_repo():
    return BookmarkRepo(mod.config.get('BOOKMARK_DB_FILE'))


@mod.record_once
def pass_config(state):
    '''configure bookmark module with app config'''
    mod.config = state.app.config.copy()


@mod.route('/', methods=['POST'])
def create_bookmark():
    '''put a new bookmark for a specific album'''
    repo = _get_repo()
    body = request.json()
    repo.put(Bookmark(**body))

    return json.dumps(repo.get(body['id']))


@mod.route('/list')
def list():
    '''list all existing bookmarks'''
    return json.dumps([b._asdict() for b in _get_repo().list()])


@mod.route('/<idx>')
def get_bookmark(idx):
    '''get a specific bookmark'''
    return json.dumps(_get_repo().get(idx)._asdict())
