"""Grasp SDK classes and utilities."""

from typing import Dict

from .server import GraspServer
from .browser import GraspBrowser
from .terminal import GraspTerminal
from .session import GraspSession
from .index import Grasp
from .utils import (
    _servers,
    shutdown,
)

# Export the global servers registry
_servers: Dict[str, GraspServer] = _servers

__all__ = [
    'GraspServer',
    'GraspBrowser', 
    'GraspTerminal',
    'GraspSession',
    'Grasp',
    'shutdown',
    '_servers',
]