'''bookmark manager functionality for podcasts and audiobooks'''
import json
from collections import namedtuple
from flask import Blueprint, request, abort
from flask_cors import CORS, cross_origin
from webplayer.dbaccess import GenericRepo

mod = Blueprint('bookmark_handler', __name__, url_prefix='/bookmark')
cors = CORS(mod)

Bookmark = namedtuple('Bookmark', ['id', 'name', 'file', 'time'])

class BookmarkRepo(GenericRepo):
    '''repo for bookmark objects'''
    def __init__(self, dbfile):
        super().__init__(dbfile, 'bookmarks', 'id', Bookmark)


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
    bookmark = _get_repo().get(idx)
    if bookmark:
        return json.dumps(bookmark._asdict())
    else:
        abort(404)


@mod.route('/<idx>', methods=['DELETE'])
@cross_origin()
def delete_list(idx):
    '''delete a specific playlist'''
    _get_repo().delete(idx)
    return ''
