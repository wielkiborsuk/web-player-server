'''scanner module for handling audio files on local drive'''
import json
import os

from collections import namedtuple
from tinydb import TinyDB, where
from flask import Blueprint, request
from flask_cors import CORS, cross_origin

mod = Blueprint('list_handler', __name__, url_prefix='/list')
cors = CORS(mod)

ListEntry = namedtuple('ListEntry', ['id', 'name', 'files'])

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


@mod.record_once
def pass_config(state):
    '''copy config from main app'''
    mod.config = state.app.config.copy()
    mod.repo = ListRepo(mod.config.get('DB_FILE'))


@mod.route('/', methods=['GET'])
def lists():
    '''return the list entries'''
    return json.dumps([d._asdict() for d in mod.repo.list()])


@mod.route('/', methods=['POST'])
def create_list():
    '''create a new list entry'''
    mod.repo.put(ListEntry(**request.json))
    return ''


@mod.route('/<idx>', methods=['PUT'])
@cross_origin()
def put_list(idx):
    '''update a specific playlist'''
    list_dict = request.json
    list_dict['id'] = idx
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
