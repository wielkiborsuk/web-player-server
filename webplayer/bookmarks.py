'''bookmark manager functionality for podcasts and audiobooks'''
from collections import namedtuple
from flask import Blueprint, request, abort, jsonify
from flask_cors import CORS, cross_origin
from webplayer.dbaccess import GenericRepo

mod = Blueprint('bookmark_handler', __name__, url_prefix='/bookmark')
cors = CORS(mod)

Bookmark = namedtuple('Bookmark', ['id', 'name', 'file', 'time'])

class BookmarkRepo(GenericRepo):
    '''repo for bookmark objects'''
    def __init__(self, dbfile):
        super().__init__(dbfile, 'bookmarks', Bookmark)


def _get_repo():
    return BookmarkRepo(mod.config.get('DB_FILE'))


def _is_after(mark_a, mark_b):
    return (mark_a.file > mark_b.file or
            (mark_a.file == mark_b.file and mark_a.time > mark_b.time))


def _save_bookmark(repo, entry, overwrite=False):
    prev = repo.get(entry.id)
    if overwrite or not (prev and _is_after(prev, entry)):
        repo.put(entry)
        return jsonify(repo.get(entry.id)._asdict()), 200

    return jsonify(repo.get(entry.id)._asdict()), 409


@mod.record_once
def pass_config(state):
    '''configure bookmark module with app config'''
    mod.config = state.app.config.copy()


@mod.route('/', methods=['POST'])
@cross_origin()
def create_bookmark():
    '''put a new bookmark for a specific album'''
    bookmark_dict = request.json
    entry = Bookmark(**bookmark_dict)
    overwrite = request.args.get('overwrite', 'false').lower() == 'true'

    return _save_bookmark(_get_repo(), entry, overwrite)


@mod.route('/')
def list_bookmarks():
    '''list all existing bookmarks'''
    return jsonify([b._asdict() for b in _get_repo().list()])


@mod.route('/<idx>', methods=['PUT'])
@cross_origin()
def put_list(idx):
    '''update a specific playlist'''
    bookmark_dict = request.json
    bookmark_dict['id'] = idx
    entry = Bookmark(**bookmark_dict)
    overwrite = request.args.get('overwrite', 'false').lower() == 'true'

    return _save_bookmark(_get_repo(), entry, overwrite)


@mod.route('/<idx>', methods=['GET'])
def get_bookmark(idx):
    '''get a specific bookmark'''
    bookmark = _get_repo().get(idx)
    if bookmark:
        return jsonify(bookmark._asdict())

    return abort(404)


@mod.route('/<idx>', methods=['DELETE'])
@cross_origin()
def delete_list(idx):
    '''delete a specific playlist'''
    _get_repo().delete(idx)
    return ''
