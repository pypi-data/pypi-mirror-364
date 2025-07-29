from cronevents.db.triggers.base import Trigger, TriggerDbBase, Generator
from cronevents.db.postgres import get_postgres_from_env, Postgres


class PostgresTriggerDb(TriggerDbBase):
    def __init__(self):
        self.db: Postgres = get_postgres_from_env()

    def insert(self, trigger: Trigger):
        self.upsert(trigger)

    def upsert(self, trigger: Trigger):
        self.db.upload_table(self.table_name, [trigger.to_row()], id_column='id')

    def list(self, stream: bool = False, cronevent_id: str | None = None) -> list[Trigger] | Generator[Trigger, None, None]:
        if cronevent_id:
            q = f'select * from {self.table_name} where cronevent_id = $id${cronevent_id}$id$ order by utc_time desc'
        else:
            q = f'select * from {self.table_name} order by utc_time desc'

        if stream:
            return (Trigger.from_row(row) for row in self.db.download_table(sql=q, stream=True))
        return [Trigger.from_row(row) for row in self.db.download_table(sql=q)]







