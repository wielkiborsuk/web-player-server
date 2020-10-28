'''bookmark manager functionality for podcasts and audiobooks'''
import json
from collections import namedtuple
from tinydb import TinyDB, where
from flask import Blueprint, request
from flask_cors import CORS, cross_origin

mod = Blueprint('bookmark_handler', __name__, url_prefix='/bookmark')
cors = CORS(mod)

Bookmark = namedtuple('Bookmark', ['id', 'file', 'time'])


class BookmarkRepo:
    '''repository used to manage bookmark objects in a database'''
    def __init__(self, dbfile):
        '''create repository using a specific database file'''
        self.table = TinyDB(dbfile).table('bookmarks')

    def put(self, bookmark:Bookmark):
        '''put new or update a bookmark'''
        self.table.upsert(bookmark._asdict(), where('id') == bookmark.id)

    def get(self, book_id) -> Bookmark:
        '''get a bookmark by book id'''
        result = self.table.search(where('id') == book_id)
        return Bookmark(**result[0]) if result else None

    def delete(self, idx):
        '''remove an entry from the table'''
        self.table.remove(where('id') == idx)

    def list(self) -> Bookmark:
        '''return all bookmarks, for debugging purposes'''
        return [Bookmark(**row) for row in self.table.all()]


def _get_repo():
    return BookmarkRepo(mod.config.get('DB_FILE'))


@mod.record_once
def pass_config(state):
    '''configure bookmark module with app config'''
    mod.config = state.app.config.copy()


@mod.route('/', methods=['POST'])
@cross_origin()
def create_bookmark():
    '''put a new bookmark for a specific album'''
    repo = _get_repo()
    body = request.json
    repo.put(Bookmark(**body))

    return json.dumps(repo.get(body['id']))


@mod.route('/')
def list_bookmarks():
    '''list all existing bookmarks'''
    return json.dumps([b._asdict() for b in _get_repo().list()])


@mod.route('/<idx>', methods=['PUT'])
@cross_origin()
def put_list(idx):
    '''update a specific playlist'''
    bookmark_dict = request.json
    bookmark_dict['id'] = idx
    entry = Bookmark(**bookmark_dict)
    _get_repo().put(entry)
    return ''


@mod.route('/<idx>', methods=['GET'])
def get_bookmark(idx):
    '''get a specific bookmark'''
    return json.dumps(_get_repo().get(idx)._asdict())


@mod.route('/<idx>', methods=['DELETE'])
@cross_origin()
def delete_list(idx):
    '''delete a specific playlist'''
    _get_repo().delete(idx)
    return ''
