import os

from cronevents.db.logs.base import LoggerBase, Log, Generator


LOG_DIR = os.environ.get('CRONEVENTS_LOG_DIR', os.path.join('.cronevents', 'logs'))
os.makedirs(LOG_DIR, exist_ok=True)


class FileLogger(LoggerBase):
    def __init__(self, trigger_id: str):
        self.trigger_id = trigger_id

    @property
    def log_file(self):
        return os.path.join(LOG_DIR, f'{self.trigger_id}.log')

    def log(self, log: str):
        with open(self.log_file, 'a') as f:
            f.write(log)
            if not log.endswith('\n'):
                f.write('\n')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def list(self, stream: bool = False) -> list[Log] | Generator[Log, None, None]:
        if stream:
            def gen():
                i = 0
                with open(self.log_file, 'r') as f:
                    for line in f:
                        yield Log(index=i, line=line.strip())
                        i += 1

            return gen()
        else:
            with open(self.log_file, 'r') as f:
                return [Log(index=i, line=line.strip()) for i, line in enumerate(f)]







