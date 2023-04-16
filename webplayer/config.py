'''config manager functionality for podcasts and audiobooks'''
from collections import namedtuple
from flask import Blueprint, request, abort, jsonify
from flask_cors import CORS, cross_origin
from webplayer.dbaccess import GenericRepo

mod = Blueprint('config_handler', __name__, url_prefix='/config')
cors = CORS(mod)

Config = namedtuple('Config', ['id', 'sources', 'settings', 'timestamp'])


class ConfigRepo(GenericRepo):
    '''repo for config objects'''
    def __init__(self, dbfile):
        super().__init__(dbfile, 'configs', Config)


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

    return jsonify(mod.repo.get(body['id'])._asdict())


@mod.route('/<idx>', methods=['GET'])
def get_bookmark(idx):
    '''get a specific config'''
    config = mod.repo.get(idx)
    if config:
        return jsonify(config._asdict())

    return abort(404)


@mod.route('/<idx>', methods=['DELETE'])
@cross_origin()
def delete_config(idx):
    '''delete a specific playlist'''
    mod.repo.delete(idx)
    return ''
