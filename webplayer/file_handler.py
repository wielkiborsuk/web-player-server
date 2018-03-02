import json
import os

from flask import Blueprint

mod = Blueprint('file_handler', __name__, url_prefix='/file')

class Cache(object):
    def __init__(self):
        self.mem = {}

    def set(self, key, value):
        self.mem[key] = value

    def get(self, key, default=None):
        return self.mem.get(key, default)

    def __contains__(self, key):
        return key in self.mem


class Scanner(object):
    audio = ['.mp3', '.ogg']

    def __init__(self):
        self.cache = Cache()

    def scan(self, path=None, url=None):
        path = path or mod.config.get('BASE_PATH', os.path.expanduser('~'))
        url = url or mod.config.get('BASE_URL', '/')

        self.cache.set('directories', self._scan(path, url))
        return self.cache.get('directories')

    def directories(self):
        return self.cache.get('directories')

    def directory(self, idx):
        dirs = self.cache.get('directories')
        return next(d for d in dirs if d['idx'] == idx)

    def _scan(self, path, url):
        albums = []
        print(path)
        for root, dirs, files in os.walk(path):
            if any([(os.path.splitext(f)[1] in self.audio) for f in files]):
                albums.append({
                    'idx': 'md5hash?',
                    'path': root.replace(path, url),
                    'files': files
                })
        return albums




scanner = Scanner()


@mod.record_once
def pass_config(state):
    mod.config = {key: value for key, value in state.app.config.items()}


@mod.route('/scan')
def scan():
    print(scanner.scan())
    return json.dumps({'status': 'ok'})


@mod.route('/')
def directories():
    return json.dumps(scanner.directories())


@mod.route('/<idx>')
def directory(idx):
    return json.dumps(scanner.directory(idx))
