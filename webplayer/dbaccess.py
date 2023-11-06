'''an attempt at generic database access'''
from typing import TypeVar, Generic, Type, List, Optional
from tinydb import TinyDB, where
from sqlalchemy import create_engine, MetaData, Table, Column, String, JSON, text, select

EntryType = TypeVar('EntryType')

class GenericTinyRepo(Generic[EntryType]):
    '''repository used to manage objects in a database'''
    def __init__(self, dbfile: str, table: str, entry_type: Type[EntryType]):
        '''create repository using a specific database file'''
        self.table = TinyDB(dbfile).table(table)
        self.entry_type = entry_type

    def put(self, obj: EntryType):
        '''put new or update an entry'''
        self.table.upsert(obj._asdict(), where('id') == obj.id)

    def get(self, idx) -> Optional[EntryType]:
        '''get an entry by id'''
        result = self.table.search(where('id') == idx)
        return self.entry_type(**result[0]) if result else None

    def delete(self, idx):
        '''remove an entry from the table'''
        self.table.remove(where('id') == idx)

    def list(self) -> List[EntryType]:
        '''return all entries, for debugging purposes usually'''
        return [self.entry_type(**row) for row in self.table.all()]

    def _query(self, key, value) -> List:
        '''return music album directories'''
        return [self.entry_type(**row) for row in self.table.search(where(key) == value)]


class GenericSqlRepo(Generic[EntryType]):
    '''repository used to manage objects in a database'''
    def __init__(self, dbfile: str, table: str, entry_type: Type[EntryType]):
        '''create repository using a specific database file'''
        self.engine = create_engine(f'sqlite:///{dbfile}')
        metadata = MetaData()
        self.table = Table(table, metadata,
                Column('id', String, primary_key=True,
                    sqlite_on_conflict_primary_key='REPLACE'),
                Column('value', JSON))
        metadata.create_all(self.engine)
        self.entry_type = entry_type

    def put(self, obj: EntryType):
        '''put new or update an entry'''
        with self.engine.begin() as conn:
            conn.execute(self.table.insert().values(id=obj.id, value=obj._asdict()))

    def get(self, idx) -> Optional[EntryType]:
        '''get an entry by id'''
        with self.engine.connect() as conn:
            result = conn.execute(select(self.table).where(text(f"id = '{idx}'"))).fetchone()
            return self.entry_type(**result[1]) if result else None

    def delete(self, idx):
        '''remove an entry from the table'''
        with self.engine.begin() as conn:
            conn.execute(self.table.delete().where(text(f"id = '{idx}'")))

    def list(self) -> List[EntryType]:
        '''return all entries, for debugging purposes usually'''
        with self.engine.connect() as conn:
            rows = conn.execute(self.table.select()).fetchall()
            return [self.entry_type(**row[1]) for row in rows]

    def _query(self, key, value) -> List:
        '''return music album directories'''
        with self.engine.connect() as conn:
            rows = conn.execute(select(self.table).where(text(f"json_extract(value, '$.{key}') = {value}"))).fetchall()
            return [self.entry_type(**row[1]) for row in rows]


GenericRepo = GenericSqlRepo
