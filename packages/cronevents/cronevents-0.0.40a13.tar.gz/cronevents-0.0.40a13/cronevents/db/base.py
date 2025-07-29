from abc import ABC, abstractmethod


class DbBase(ABC):
    table_name: str

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def get(self, *args):
        pass

    @abstractmethod
    def set(self, *args, **kwargs):
        pass










