import datetime

import psycopg2

from cronevents.db.cronevents.base import CronEvent, CronEventsDbBase
from cronevents.db.postgres import get_postgres_from_env, Postgres
from cronevents.errors.exceptions import CronEventValueError


class PostgresCronEventsDb(CronEventsDbBase):
    table_name: str = 'cronevents'

    def __init__(self):
        self.db: Postgres = get_postgres_from_env()

    def upsert(self, cronevent: CronEvent) -> None:
        if isinstance(cronevent.last, datetime.datetime):
            cronevent.last = cronevent.last.isoformat()
        self.db.upload_table(self.table_name, [cronevent.to_row()], id_column=['id'])

    def insert(self, cronevent: CronEvent) -> None:
        self.upsert(cronevent)

    def update(self, cronevent: CronEvent) -> None:
        self.upsert(cronevent)

    @staticmethod
    def get_quotes(text: str):
        q = 'id'
        i = 0
        while f'${q}$' in text:
            i += 1
            q = f'id{i}'
        return f'${q}$'

    def delete(self, cronevent_id: str) -> None:
        q = self.get_quotes(cronevent_id)
        try:
            self.db.query(f'DELETE FROM {self.table_name} WHERE id = {q}{cronevent_id}{q};')
        except psycopg2.errors.UndefinedTable: pass

    @staticmethod
    def fix_row(row: dict):
        if isinstance(row['last'], str):
            row['last'] = datetime.datetime.fromisoformat(row['last'])
            row['last'] = row['last'].replace(tzinfo=datetime.timezone.utc)
        return row

    def get(self, cronevent_id: str | None = None, module: str | None = None, func: str | None = None) -> CronEvent | None:
        if cronevent_id is None and (module is None or func is None):
            raise CronEventValueError('At least one of cronevent_id or (module and func) must be provided')

        if cronevent_id:
            q = self.get_quotes(cronevent_id)
            where = f'WHERE id = {q}{cronevent_id}{q}'
        else:
            q = self.get_quotes(module + func)
            where = f'WHERE module = {q}{module}{q} AND func = {q}{func}{q}'

        try:
            table = self.db.download_table(sql=f'SELECT * FROM {self.table_name} {where};')
        except psycopg2.errors.UndefinedTable:
            table = []

        if not table:
            return None
        row = table[0]
        return CronEvent(**self.fix_row(row))

    def list(self) -> list[CronEvent]:
        try:
            table = self.db.download_table(self.table_name)
        except psycopg2.errors.UndefinedTable:
            table = []

        return [CronEvent(**self.fix_row(row)) for row in table]






