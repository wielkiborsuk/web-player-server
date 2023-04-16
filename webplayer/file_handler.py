'''scanner module for handling audio files on local drive'''
import os
import hashlib

from collections import namedtuple
from flask import Blueprint, jsonify
from flask_cors import CORS, cross_origin
from webplayer.dbaccess import GenericRepo

mod = Blueprint('file_handler', __name__, url_prefix='/file')
cors = CORS(mod)

DirectoryEntry = namedtuple('DirectoryEntry', ['id', 'name', 'path', 'url', 'files', 'is_book'])

class DirectoryRepo(GenericRepo):
    '''repository for Directory objects'''
    def __init__(self, dbfile):
        super().__init__(dbfile, 'directories', DirectoryEntry)

    def albums(self) -> list:
        '''return music album directories'''
        return self._query('is_book', 0)

    def books(self) -> list:
        '''return audio book directories'''
        return self._query('is_book', 1)



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

    def albums(self):
        '''return scanned and cached directories'''
        return self.cache.albums()

    def books(self):
        '''return scanned and cached directories'''
        return self.cache.books()

    def directory(self, idx):
        '''return a specific scanned directory entry'''
        return self.cache.get(idx)

    def clear(self, idx):
        '''clear cached directory'''
        self.cache.delete(idx)

    def _scan(self, path, url, look_for_books=False):
        for root, directories, files in os.walk(path):
            base_url = root.replace(path, url)
            if not look_for_books and '.nomedia' in files:
                directories[:] = []
                self._scan(root, base_url, look_for_books=True)
                continue
            if any([(os.path.splitext(f)[1] in self.audio) for f in files]):
                files = sorted([f for f in files if os.path.splitext(f)[1] in self.audio])
                entry = DirectoryEntry(self._hashsum(root), os.path.basename(root),
                        root, base_url, self._get_files(files, base_url), look_for_books)
                self.cache.put(entry)

    @staticmethod
    def _get_files(files, base_url):
        return [{'name': file_name, 'url': f'{base_url}/{file_name}'}
                for file_name in files]

    @staticmethod
    def _hashsum(path):
        '''calculate hashsum for a path as a unique identifier'''
        return hashlib.md5(path.encode('utf-8')).hexdigest()




@mod.record_once
def pass_config(state):
    '''copy config from main app'''
    mod.config = state.app.config.copy()
    mod.scanner = Scanner(DirectoryRepo(mod.config.get('DB_FILE')))

@mod.route('/scan')
def scan():
    '''scan default directories'''
    return jsonify([d._asdict() for d in mod.scanner.scan()])


@mod.route('/')
@cross_origin()
def albums():
    '''return the already scanned directory entries'''
    return jsonify([d._asdict() for d in mod.scanner.albums()])


@mod.route('/book/')
@cross_origin()
def books():
    '''return the already scanned directory entries'''
    return jsonify([d._asdict() for d in mod.scanner.books()])


@mod.route('/<idx>', methods=['GET'])
@cross_origin()
def get_directory(idx):
    '''return a specific directory playlist'''
    return jsonify(mod.scanner.directory(idx)._asdict())


@mod.route('/<idx>', methods=['DELETE'])
@cross_origin()
def delete_directory(idx):
    '''delete a specific cached directory playlist'''
    mod.scanner.clear(idx)
    return ''
