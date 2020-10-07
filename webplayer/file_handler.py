'''scanner module for handling audio files on local drive'''
import json
import os
import hashlib

from collections import namedtuple
from tinydb import TinyDB, where
from flask import Blueprint

mod = Blueprint('file_handler', __name__, url_prefix='/file')

DirectoryEntry = namedtuple('DirectoryEntry', ['id', 'name', 'path', 'url', 'files'])

class DirectoryRepo:
    '''repository used to manage scanned directories objects in a database'''
    def __init__(self, dbfile):
        '''create repository using a specific database file'''
        self.dataase = TinyDB(dbfile)

    def put(self, directory:DirectoryEntry):
        '''put new or update a directory entry'''
        self.dataase.upsert(directory._asdict(), where('id') == directory.id)

    def get(self, absolute_path) -> DirectoryEntry:
        '''get a directory entry by absolute path'''
        result = self.dataase.search(where('id') == absolute_path)
        return DirectoryEntry(**result[0]) if result else None

    def list(self) -> DirectoryEntry:
        '''return all directories, for debugging purposes'''
        return [DirectoryEntry(**row) for row in self.dataase.all()]


class Scanner:
    '''scanner service, looking for audio files on local drive'''
    audio = ['.mp3', '.ogg', '.m4a']

    def __init__(self, directory_repo):
        self.cache = directory_repo

    def scan(self, path=None, url=None):
        '''scan local drive looking for audio files, provide base url to serve them from'''
        path = path or mod.config.get('BASE_PATH', os.path.expanduser('~'))
        url = url or mod.config.get('BASE_URL', '/')

        self._scan(path, url)
        return self.cache.list()

    def directories(self):
        '''return scanned and cached directories'''
        return self.cache.list()

    def directory(self, idx):
        '''return a specific scanned directory entry'''
        return self.cache.get(idx)

    def _scan(self, path, url):
        for root, _, files in os.walk(path):
            if any([(os.path.splitext(f)[1] in self.audio) for f in files]):
                entry = DirectoryEntry(self._hashsum(root), os.path.basename(root),
                        root, root.replace(path, url), files)
                self.cache.put(entry)

    @staticmethod
    def _hashsum(path):
        '''calculate hashsum for a path as a unique identifier'''
        return hashlib.md5(path.encode('utf-8')).hexdigest()




@mod.record_once
def pass_config(state):
    '''copy config from main app'''
    mod.config = state.app.config.copy()
    mod.scanner = Scanner(DirectoryRepo(mod.config.get('DIRECTORY_DB_FILE')))

@mod.route('/scan')
def scan():
    '''scan default directories'''
    mod.scanner.scan()
    return directories()


@mod.route('/')
def directories():
    '''return the already scanned directory entries'''
    return json.dumps([d._asdict() for d in mod.scanner.directories()])


@mod.route('/<idx>')
def get_directory(idx):
    '''return a specific directory playlist'''
    return json.dumps(mod.scanner.directory(idx)._asdict())
