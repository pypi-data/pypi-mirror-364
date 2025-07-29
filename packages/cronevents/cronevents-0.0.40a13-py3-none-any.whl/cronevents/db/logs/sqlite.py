import time
import queue
import datetime
import threading

from cronevents.db.logs.base import LoggerBase, Log, Generator
from cronevents.db.sqlite import Sqlite3


class Sqlite3Logger(LoggerBase):
    table_name: str = 'cronevents_log'

    def __init__(self, trigger_id):
        self.trigger_id = trigger_id
        self.db = Sqlite3()

        self.queue = queue.Queue()
        self.current_index = -1
        self.last_log = time.time()

        self.thread = None

        self.__pinging = False
        self.pinger_thread = None

    def start_logger(self):
        self.thread = threading.Thread(target=self.logger)
        self.thread.start()

        self.pinger_thread = threading.Thread(target=self.pinger, daemon=True)
        self.pinger_thread.start()

    def stop_logger(self):
        self.__pinging = False
        self.queue.put(None)

        if self.thread:
            self.thread.join()
            self.thread = None

        if self.pinger_thread:
            self.pinger_thread.join()
            self.pinger_thread = None

        self.ping()

    def __del__(self):
        self.stop_logger()

    def __enter__(self):
        self.start_logger()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_logger()
        if exc_type:
            print('exc_type', exc_type)
            print('exc_val', exc_val)
            print('exc_tb', exc_tb)

    def create_row(self, logs: list[str] | list[tuple[str, float]]):
        for log in logs:
            self.current_index += 1

            if isinstance(log, tuple):
                log, t = log
            else:
                t = time.time()

            # yield {
            #     'trigger_id': self.trigger_id,
            #     'index': self.current_index,
            #     'line': log,
            #     # 'epoch': t,
            #     'utc_time': datetime.datetime.fromtimestamp(time.time(), tz=datetime.timezone.utc),
            #     # datetime.datetime.fromtimestamp(t, datetime.UTC)
            # }

            yield Log(
                trigger_id=self.trigger_id,
                index=self.current_index,
                line=log,
                utc_time=datetime.datetime.fromtimestamp(t, datetime.timezone.utc),
            ).to_row()

    def upload(self, logs: list[str] | list[tuple[str, float]]):
        table = list(self.create_row(logs))
        self.upload_to_db(table)

    def upload_to_db(self, table):
        upload_logs(self.db, self.trigger_id, table)

    def log(self, s):
        self.queue.put(s)

    def logger(self):
        current_log = []
        while True:
            log = self.queue.get()
            if log is None:
                break

            current_log.append((log, time.time()))

            if time.time() - self.last_log > 1 or len(current_log) > 100:
                self.upload(current_log)
                current_log = []
                self.last_log = time.time()

        if current_log:
            self.upload(current_log)

    def ping(self):
        # row = {
        #     'trigger_id': self.trigger_id,
        #     'index': -1,
        #     'line': 'ping',
        #     'utc_time': datetime.datetime.fromtimestamp(time.time(), tz=datetime.timezone.utc),
        # }
        row = Log(
            trigger_id=self.trigger_id,
            index=-1,
            line='ping',
            utc_time=datetime.datetime.fromtimestamp(time.time(), tz=datetime.timezone.utc),
        ).to_row()
        self.upload_to_db([row])

    __pinging = False

    def pinger(self):
        self.__pinging = True

        while self.__pinging:
            self.ping()
            time.sleep(60 * 5)

    def list(self, stream: bool = False) -> list[Log] | Generator[Log, None, None]:
        q = f"select * from {self.table_name} where trigger_id = '{self.trigger_id}' order by index asc;"
        if stream:
            return (Log.from_row(row) for row in self.db.download_table(sql=q, stream=True, return_empty_table_on_fail=True))
        return [Log.from_row(row) for row in self.db.download_table(sql=q, return_empty_table_on_fail=True)]


def upload_logs(db: Sqlite3, trigger_id, logs):
    if logs:
        index_query = f'create index if not exists event_logs_event_id_idx on {Sqlite3Logger.table_name} (trigger_id);'

        db.upload_table(
            Sqlite3Logger.table_name,
            logs,
            id_column=['trigger_id', 'index'],
        )
        db.query(index_query)

