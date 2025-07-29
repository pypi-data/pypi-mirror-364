import time
import json
import datetime
import importlib
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from cronevents.errors.exceptions import CronEventValidationError


@dataclass
class CronEvent:
    query: str
    module: str
    func: str
    args: str
    kwargs: str
    id: str | None = None
    last: datetime.datetime | None = field(default_factory=lambda: datetime.datetime.fromtimestamp(time.time(), tz=datetime.timezone.utc))

    def display(self):
        t = ''
        if isinstance(self.last, datetime.datetime):
            t = ' | ' + self.last.strftime('%Y-%m-%d %H:%M:%S')
        return f'{self.id}{t} | {self.module}.{self.func}({self.args}, {self.kwargs})'

    def __post_init__(self):
        if self.id is None:
            self.id = f'{self.module}|{self.func}'
        if self.last is None:
            self.last = datetime.datetime.fromtimestamp(time.time(), tz=datetime.timezone.utc)

    def clone(self, **kwargs):
        return CronEvent(**{**self.to_row(), **kwargs})

    def to_row(self):
        # self.validate()
        return {
            'id': self.id,
            'module': self.module,
            'func': self.func,
            'query': self.query,
            'args': self.args,
            'kwargs': self.kwargs,
            'last': self.last
        }

    def validate(self):
        from cronevents.event_manager import query_syntax_checker

        if not isinstance(self.id, str):
            raise CronEventValidationError(f'Invalid id: {self.id}. Must be string.')

        # try:
        #     mod = importlib.import_module(self.module)
        # except:
        #     raise CronEventValidationError(f'Invalid module: {self.module}')

        # if not hasattr(mod, self.func) or not callable(getattr(mod, self.func)):
        #     raise CronEventValidationError(f'Invalid function: {self.func}')

        try:
            json.loads(self.args)
        except:
            raise CronEventValidationError(f'Invalid args: {self.args}. Must be json.')

        try:
            json.loads(self.kwargs)
        except:
            raise CronEventValidationError(f'Invalid kwargs: {self.kwargs}. Must be json.')

        if self.last.tzinfo != datetime.timezone.utc:
            raise CronEventValidationError(f'Invalid last.tzinfo: {self.last.tzinfo}. Must be `datetime.timezone.utc`.')

        query_syntax_checker(self.query)

        return True


class CronEventsDbBase(ABC):
    table_name: str = 'cronevents'

    @abstractmethod
    def insert(self, cronevent: CronEvent) -> None:
        pass

    @abstractmethod
    def update(self, cronevent: CronEvent) -> None:
        pass

    @abstractmethod
    def upsert(self, cronevent: CronEvent) -> None:
        pass

    @abstractmethod
    def delete(self, cronevent_id: str) -> None:
        pass

    @abstractmethod
    def get(self, cronevent_id: str | None = None, module: str | None = None, func: str | None = None) -> CronEvent | None:
        pass

    @abstractmethod
    def list(self) -> list[CronEvent]:
        pass






