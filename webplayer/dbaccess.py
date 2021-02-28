'''an attempt at generic database access'''
from typing import TypeVar, Generic, Type, List
from tinydb import TinyDB, where
from sqlalchemy import create_engine, MetaData, Table, Column, String, JSON, text

EntryType = TypeVar('EntryType')

class GenericTinyRepo(Generic[EntryType]):
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

    def _query(self, key, value) -> list:
        '''return music album directories'''
        return [self.entry_type(**row) for row in self.table.search(where(key) == value)]


class GenericSqlRepo(Generic[EntryType]):
    '''repository used to manage objects in a database'''
    def __init__(self, dbfile: str, table: str, idx_name: str, entry_type: Type[EntryType]):
        '''create repository using a specific database file'''
        self.engine = create_engine('sqlite:///{}'.format(dbfile))
        metadata = MetaData()
        self.table = Table(table, metadata,
                Column(idx_name, String, primary_key=True,
                    sqlite_on_conflict_primary_key='REPLACE'),
                Column('value', JSON))
        metadata.create_all(self.engine)
        self.entry_type = entry_type
        self.idx_name = idx_name

    def put(self, obj: EntryType):
        '''put new or update an entry'''
        with self.engine.connect() as conn:
            conn.execute(self.table.insert(), {self.idx_name: obj.id, 'value': obj._asdict()})

    def get(self, idx) -> EntryType:
        '''get an entry by id'''
        with self.engine.connect() as conn:
            result = conn.execute(self.table.select(text("{} = '{}'".format(self.idx_name, idx)))).fetchone()
            return self.entry_type(**result['value']) if result else None

    def delete(self, idx):
        '''remove an entry from the table'''
        with self.engine.connect() as conn:
            conn.execute(self.table.delete(text("{} = '{}'".format(self.idx_name, idx))))

    def list(self) -> List[EntryType]:
        '''return all entries, for debugging purposes usually'''
        with self.engine.connect() as conn:
            rows = conn.execute(self.table.select()).fetchall()
            return [self.entry_type(**row['value']) for row in rows]

    def _query(self, key, value) -> list:
        '''return music album directories'''
        with self.engine.connect() as conn:
            rows = conn.execute(self.table.select(text("json_extract(value, '$.{}') = {}".format(key, value)))).fetchall()
            return [self.entry_type(**row['value']) for row in rows]


GenericRepo = GenericSqlRepo
