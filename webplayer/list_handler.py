'''scanner module for handling audio files on local drive'''
import json
from collections import namedtuple
import yaml

from tinydb import TinyDB, where
from flask import Blueprint, request
from flask_cors import CORS, cross_origin

mod = Blueprint('list_handler', __name__, url_prefix='/list')
cors = CORS(mod)

ListEntry = namedtuple('ListEntry', ['id', 'name', 'files', 'is_book'])

class ListRepo:
    '''repository used to manage handmage playlist objects in a database'''
    def __init__(self, dbfile):
        '''create repository using a specific database file'''
        self.table = TinyDB(dbfile).table('lists')

    def put(self, list_obj:ListEntry):
        '''put new or update a directory entry'''
        self.table.upsert(list_obj._asdict(), where('id') == list_obj.id)

    def get(self, idx) -> ListEntry:
        '''get an entry by id'''
        result = self.table.search(where('id') == idx)
        return ListEntry(**result[0]) if result else None

    def delete(self, idx):
        '''remove an entry from the table'''
        self.table.remove(where('id') == idx)

    def list(self) -> ListEntry:
        '''return all directories, for debugging purposes'''
        return [ListEntry(**row) for row in self.table.all()]

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
        url_map = yaml.load(url_file)
        for k,v in url_map.items():
            file_list = sorted([{'name': entry['filename'], 'url': entry['url']}
                for entry in v], key=lambda e: e['name'])
            entry = ListEntry(k, k, file_list, True)
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
