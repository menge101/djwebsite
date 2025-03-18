from threading import Thread
from typing import Any, Callable, Mapping


class ThreadException(BaseException):
    pass


class ThreadExit(SystemExit):
    pass


class ReturningThread(Thread):
    def __init__(
        self,
        target: Callable,
        name: str | None = None,
        args: tuple = (),
        kwargs: Mapping | None = None,
        *,
        daemon: bool | None = None,
    ):
        super().__init__(
            group=None,
            target=target,
            name=name,
            args=args,
            kwargs=kwargs,
            daemon=daemon,
        )
        self.return_value: Any | None = None
        self.exception: Exception | None = None

    def run(self):
        try:
            if self._target is not None:
                try:
                    self.return_value = self._target(*self._args, **self._kwargs)
                except Exception as e:
                    self.exception = e
        finally:
            del self._target, self._args, self._kwargs

    def join(self, *args) -> Any | None:
        if self.exception is not None:
            raise self.exception
        super().join(*args)
        return self.return_value

    def start_safe(self, *args):
        if not self._started.is_set():
            self.start(*args)

    def stop(self):
        raise ThreadExit(0)
