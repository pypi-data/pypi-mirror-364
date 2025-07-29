import time
import datetime
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
from typing import Generator


@dataclass
class Trigger:
    id: str
    cronevent_id: str
    pid: str
    module: str
    func: str
    args: str
    kwargs: str
    utc_time: datetime.datetime = field(default_factory=lambda: datetime.datetime.fromtimestamp(time.time(), tz=datetime.timezone.utc))

    def display(self):
        t = ''
        if isinstance(self.utc_time, datetime.datetime):
            t = '[' + self.utc_time.strftime('%Y-%m-%d %H:%M:%S') + '] '
        return f'{t}id: {self.id}, pid: {self.pid}, module: {self.module}, function: {self.func}({self.args}, {self.kwargs})'

    def to_row(self):
        return asdict(self)

    @classmethod
    def from_row(cls, row: dict):
        return cls(**row)


class TriggerDbBase(ABC):
    table_name: str = 'cronevents_triggers'

    @abstractmethod
    def insert(self, trigger: Trigger):
        pass

    @abstractmethod
    def upsert(self, trigger: Trigger):
        pass

    @abstractmethod
    def list(self, stream: bool = False, cronevent_id: str | None = None) -> list[Trigger] | Generator[Trigger, None, None]:
        pass







