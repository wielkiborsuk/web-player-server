'''config manager functionality for podcasts and audiobooks'''
import json
from collections import namedtuple
from tinydb import TinyDB, where
from flask import Blueprint, request
from flask_cors import CORS, cross_origin

mod = Blueprint('config_handler', __name__, url_prefix='/config')
cors = CORS(mod)

Config = namedtuple('Config', ['id', 'sources', 'settings', 'timestamp'])


class ConfigRepo:
    '''repository used to manage user config objects in a database'''
    def __init__(self, dbfile):
        '''create repository using a specific database file'''
        self.table = TinyDB(dbfile).table('configs')

    def put(self, config:Config):
        '''put new or update a config'''
        self.table.upsert(config._asdict(), where('id') == config.id)

    def get(self, idx) -> Config:
        '''get a config by book id'''
        result = self.table.search(where('id') == idx)
        return Config(**result[0]) if result else None

    def delete(self, idx):
        '''remove an entry from the table'''
        self.table.remove(where('id') == idx)

    def list(self) -> list:
        '''return all bookmarks, for debugging purposes'''
        return [Config(**row) for row in self.table.all()]


@mod.record_once
def pass_config(state):
    '''configure config module with app config'''
    mod.config = state.app.config.copy()
    mod.repo = ConfigRepo(mod.config.get('DB_FILE'))


@mod.route('/', methods=['POST'])
@cross_origin()
def create_config():
    '''put a new config for a specific album'''
    body = request.json
    mod.repo.put(Config(**body))

    return json.dumps(mod.repo.get(body['id']))


@mod.route('/<idx>', methods=['GET'])
def get_bookmark(idx):
    '''get a specific config'''
    return json.dumps(mod.repo.get(idx)._asdict())


@mod.route('/<idx>', methods=['DELETE'])
@cross_origin()
def delete_config(idx):
    '''delete a specific playlist'''
    mod.repo.delete(idx)
    return ''
