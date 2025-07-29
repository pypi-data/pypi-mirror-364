"""
CoTyper.

wrapper lib for Typer to use recursive nested pydantic.BaseModels as parameters
"""

from .compose.fold import unfold_cls
from .methods.parse import parse_json_fields
from .parser.app import App as App

__all__ = [
    "unfold_cls",
    "parse_json_fields",
    "App",
]
