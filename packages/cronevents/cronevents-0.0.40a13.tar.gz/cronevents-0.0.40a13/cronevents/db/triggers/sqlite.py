from cronevents.db.triggers.base import Trigger, TriggerDbBase, Generator
from cronevents.db.sqlite import Sqlite3


class Sqlite3TriggerDb(TriggerDbBase):
    def __init__(self):
        self.db: Sqlite3 = Sqlite3()

    def insert(self, trigger: Trigger):
        self.upsert(trigger)

    def upsert(self, trigger: Trigger):
        self.db.upload_table(self.table_name, [trigger.to_row()], id_column='id')

    def list(self, stream: bool = False, cronevent_id: str | None = None) -> list[Trigger] | Generator[Trigger, None, None]:
        if cronevent_id:
            q = f'select * from {self.table_name} where cronevent_id = \'{cronevent_id}\' order by utc_time desc'
        else:
            q = f'select * from {self.table_name} order by utc_time desc'

        if stream:
            return (Trigger.from_row(row) for row in self.db.download_table(sql=q, stream=True, return_empty_table_on_fail=True))
        return [Trigger.from_row(row) for row in self.db.download_table(sql=q, return_empty_table_on_fail=True)]






