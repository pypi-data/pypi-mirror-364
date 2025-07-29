import datetime
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Generator


@dataclass
class Log:
    index: int
    line: str
    trigger_id: str | None = None
    utc_time: datetime.datetime | None = None

    def display(self):
        t = ''
        if isinstance(self.utc_time, datetime.datetime):
            t = ' | ' + self.utc_time.strftime('%Y-%m-%d %H:%M:%S')
        return f'{self.index:5d}{t} | {self.line}'

    def to_row(self, datetime_ok: bool = False):
        utc = self.utc_time
        if isinstance(utc, datetime.datetime):
            if not datetime_ok:
                utc = self.utc_time.isoformat()
        return {
            'trigger_id': self.trigger_id,
            'index': self.index,
            'line': self.line,
            'utc_time': utc
        }

    @classmethod
    def from_row(cls, row: dict):
        if isinstance(row['utc_time'], str):
            row['utc_time'] = datetime.datetime.fromisoformat(row['utc_time'])
            row['utc_time'] = row['utc_time'].replace(tzinfo=datetime.timezone.utc)

        return cls(
            trigger_id=row['trigger_id'],
            index=row['index'],
            line=row['line'],
            utc_time=row['utc_time']
        )


class LoggerBase(ABC):
    @abstractmethod
    def __init__(self, trigger_id: str): pass

    @abstractmethod
    def log(self, log: str): pass

    def __enter__(self):
        return self

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb): pass

    @abstractmethod
    def list(self, stream: bool = False) -> list[Log] | Generator[Log, None, None]:
        pass


class MockLogger(LoggerBase):
    def __init__(self, *args, **kwargs): pass

    def log(self, *args, **kwargs): pass

    def __enter__(self): return self

    def __exit__(self, exc_type, exc_val, exc_tb): pass

    def list(self, stream: bool = False) -> list[Log]:
        return []



