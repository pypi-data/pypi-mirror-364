"""
CoTyper.

wrapper lib for Typer to use recursive nested pydantic.BaseModels as parameters
"""

from cotyper.compose.fold import unfold_cls
from cotyper.methods.parse import parse_json_fields
from cotyper.parser.app import App as App

__all__ = [
    "unfold_cls",
    "parse_json_fields",
    "App",
]
