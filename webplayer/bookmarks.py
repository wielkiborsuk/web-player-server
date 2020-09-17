from tinydb import TinyDB, Query, where
from tinydb.table import Document

class BookmarkRepo:

    def __init__(self, dbfile):
        self.db = TinyDB(dbfile)

    def create(self, bookmark):
        self.db.upsert(bookmark, where('id') == bookmark['id'])

    def put(self, bookmark):
        self.db.upsert(bookmark, where('id') == bookmark['id'])

    def get(self, book_id):
        book = Query()
        return self.db.search(book.id == book_id)

    def list(self):
        return self.db.all()


def main():
    repo = BookmarkRepo('testdb.json')
    print(repo.db)
    # repo.db.truncate()
    repo.create({'id': 'hello.internet', 'file': 'hi133.mp3', 'time': 12323123})
    print(repo.db)
    print(repo.get('hello.internet'))

if __name__ == '__main__':
    main()
