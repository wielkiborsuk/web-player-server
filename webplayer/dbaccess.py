'''an attempt at generic database access'''
from typing import TypeVar, Generic, Type, List
from tinydb import TinyDB, where

EntryType = TypeVar('EntryType')

class GenericRepo(Generic[EntryType]):
    '''repository used to manage objects in a database'''
    def __init__(self, dbfile: str, table: str, idx_name: str, entry_type: Type[EntryType]):
        '''create repository using a specific database file'''
        self.table = TinyDB(dbfile).table(table)
        self.entry_type = entry_type
        self.idx_name = idx_name

    def put(self, obj: EntryType):
        '''put new or update an entry'''
        self.table.upsert(obj._asdict(), where(self.idx_name) == obj.id)

    def get(self, idx) -> EntryType:
        '''get an entry by id'''
        result = self.table.search(where(self.idx_name) == idx)
        return self.entry_type(**result[0]) if result else None

    def delete(self, idx):
        '''remove an entry from the table'''
        self.table.remove(where(self.idx_name) == idx)

    def list(self) -> List[EntryType]:
        '''return all entries, for debugging purposes usually'''
        return [self.entry_type(**row) for row in self.table.all()]
