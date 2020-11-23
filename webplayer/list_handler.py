'''scanner module for handling audio files on local drive'''
import json
from collections import namedtuple
import yaml

from tinydb import where
from flask import Blueprint, request
from flask_cors import CORS, cross_origin
from webplayer.dbaccess import GenericRepo

mod = Blueprint('list_handler', __name__, url_prefix='/list')
cors = CORS(mod)

ListEntry = namedtuple('ListEntry', ['id', 'name', 'files', 'is_book'])

class ListRepo(GenericRepo):
    '''repo for editable list objects'''
    def __init__(self, dbfile):
        super().__init__(dbfile, 'lists', 'id', ListEntry)

    def lists(self) -> ListEntry:
        '''return editable playlists'''
        return [ListEntry(**row) for row in self.table.search(where('is_book') == False)]

    def books(self) -> ListEntry:
        '''return book/podcast saved entries'''
        return [ListEntry(**row) for row in self.table.search(where('is_book') == True)]


def load_podcasts(repo, podcast_file):
    '''load podcasts from selected podcatcher yaml export'''
    if not podcast_file:
        return

    with open(podcast_file, 'r') as url_file:
        url_map = yaml.safe_load(url_file)
        for key,value in url_map.items():
            file_list = sorted([{'name': entry['filename'], 'url': entry['url']}
                for entry in value], key=lambda e: e['name'])
            entry = ListEntry(key, key, file_list, True)
            repo.put(entry)



@mod.record_once
def pass_config(state):
    '''copy config from main app'''
    mod.config = state.app.config.copy()
    mod.repo = ListRepo(mod.config.get('DB_FILE'))
    load_podcasts(mod.repo, mod.config.get('PODCAST_FILE'))


@mod.route('/book/', methods=['GET'])
def podcasts():
    '''return the book/podcast entries'''
    return json.dumps([d._asdict() for d in mod.repo.books()])


@mod.route('/', methods=['GET'])
def lists():
    '''return the list entries'''
    return json.dumps([d._asdict() for d in mod.repo.lists()])


@mod.route('/', methods=['POST'])
def create_list():
    '''create a new list entry'''
    body = request.json
    body['is_book'] = False
    mod.repo.put(ListEntry(**body))
    return ''


@mod.route('/<idx>', methods=['PUT'])
@cross_origin()
def put_list(idx):
    '''update a specific playlist'''
    list_dict = request.json
    list_dict['id'] = idx
    list_dict['is_book'] = False
    entry = ListEntry(**list_dict)
    mod.repo.put(entry)
    return ''


@mod.route('/<idx>', methods=['GET'])
@cross_origin()
def get_list(idx):
    '''return a specific playlist'''
    return json.dumps(mod.repo.get(idx)._asdict())


@mod.route('/<idx>', methods=['DELETE'])
@cross_origin()
def delete_list(idx):
    '''delete a specific playlist'''
    mod.repo.delete(idx)
    return ''
