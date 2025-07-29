import os
import sys
import yaml
import importlib
from typing import Type

from cronevents.db.cronevents.base import CronEventsDbBase
from cronevents.db.cronevents.sqlite import Sqlite3CronEventsDb
from cronevents.db.logs.base import LoggerBase
from cronevents.db.logs.file import FileLogger
from cronevents.db.triggers.base import TriggerDbBase
from cronevents.db.triggers.sqlite import Sqlite3TriggerDb


sys.path.insert(0, os.getcwd())  # <-- for cli tool

_settings: dict | None = None
settings_path = os.environ.get('CRONEVENTS_SETTINGS_PATH', os.path.join('.cronevents', 'settings.yaml'))
dir_name = os.path.dirname(settings_path)
if not os.path.exists(dir_name) and settings_path not in {'.', '', './', '/'}:
    os.makedirs(dir_name)


def init():
    global _settings

    try:
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                _settings = yaml.safe_load(f)
        else:
            _settings = default_settings
            with open(settings_path, 'w') as f:
                yaml.dump(_settings, f)
    except Exception as e:
        print('Error while reading settings file:', e)

    if not isinstance(_settings, dict):
        _settings = {}


class DbConfig:
    def __init__(self, module: str, name: str, base_class, default_class):
        self.default_class = default_class
        try:
            mod = importlib.import_module(module)
            if hasattr(mod, name):
                cls = getattr(mod, name)
                if isinstance(cls, base_class) or issubclass(cls, base_class):
                    self.cls = cls
                    return
                else:
                    print(f'Class {name} in module {module} is not a subclass of {base_class}')
            else:
                print(f'No class {name} in module {module}')
        except Exception as e:
            pass
            print('Error while loading db:', e)
        self.cls = default_class


default_settings = {
    'log_cronevents_triggers': True,
    'log_cronevents_processes': False,
    'cronevents': {
        'module': 'cronevents.db.cronevents.sqlite',
        'name': 'Sqlite3CronEventsDb'
    },
    'logger': {
        'module': 'cronevents.db.logs.file',
        'name': 'FileLogger'
    },
    'trigger': {
        'module': 'cronevents.db.triggers.sqlite',
        'name': 'Sqlite3TriggerDb'
    }
}


class Settings:
    log_cronevents_triggers: bool = True
    log_cronevents_processes: bool = True

    cronevents: CronEventsDbBase
    logger: Type[LoggerBase]
    trigger: TriggerDbBase

    def __init__(
            self,
            log_cronevents_triggers: bool = True,
            log_cronevents_processes: bool = False,

            cronevents: dict = None,
            logger: dict = None,
            trigger: dict = None,
            **kwargs
    ):
        self.log_cronevents_triggers = log_cronevents_triggers
        self.log_cronevents_processes = log_cronevents_processes

        config = DbConfig(**cronevents, base_class=CronEventsDbBase, default_class=Sqlite3CronEventsDb)
        self.cronevents = config.cls()

        config = DbConfig(**logger, base_class=LoggerBase, default_class=FileLogger)
        self.logger = config.cls

        config = DbConfig(**trigger, base_class=TriggerDbBase, default_class=Sqlite3TriggerDb)
        self.trigger = config.cls()


# init()
settings: Settings | None = None  # Settings(**{**default_settings, **_settings})


def get_settings() -> Settings:
    global settings

    if not settings:
        init()
        settings = Settings(**{**default_settings, **_settings})

    return settings






