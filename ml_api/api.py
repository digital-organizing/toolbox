from __future__ import annotations

from typing import Any, Callable, Coroutine, Dict, List, TYPE_CHECKING

from ml_api.base_command import Command
from ml_api.base_result import Result

if TYPE_CHECKING:
    from ml_api.server import Server

HANDLERS: Dict[str, Callable[[Command, Server], Result | Coroutine[Any, Any, Result]]] = {}


def register_handler(name: str):

    def wrapper(func: Callable[[Command, Server], Result | Coroutine[Any, Any, Result]]):
        HANDLERS[name] = func
        return func

    return wrapper


class ListCommand(Command):
    name = 'list'


class ListResult(Result):
    handlers: List[str]

    def __init__(self, handlers) -> None:
        super().__init__()
        self.handlers = list(handlers)


@register_handler(ListCommand.name)
def list_handlers(_: Command, _server: Server):
    return ListResult(HANDLERS.keys())


class ConnectCommand(Command):
    name = "connect"


class ConnectionEstablished(Result):
    pass


class ErrorResult(Result, Exception):

    def __init__(self, err):
        self.err = err


@register_handler(ConnectCommand.name)
def connect(cmd, server):
    return ConnectionEstablished()
