import inspect
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, TypeVar

from docstring_parser import Docstring, DocstringParam, parse
from pydantic import BaseModel

T = TypeVar("T", bound=Any)


def is_in(value: Any, values: set[Any] | None = None) -> bool:
    return True if values is None else value in values


@dataclass(frozen=True)
class BaseModelParameter:
    name: str
    annotation: Type[T]
    default: Optional[T] = None
    doc: str = ""


def get_docstring(cls: type) -> str:
    return cls.__doc__


def parse_docstring(cls: type) -> Docstring:
    return parse(get_docstring(cls))


def get_param_doc(
    doc_string: Docstring, *, param_names: set[str] | None = None
) -> dict[str, DocstringParam]:
    return {
        param.arg_name: param
        for param in doc_string.params
        if is_in(param.arg_name, param_names)
    }


def getdoc(klass: Type[BaseModel]) -> Dict[str, BaseModelParameter]:
    signature = inspect.signature(klass)
    docs = get_param_doc(
        parse_docstring(klass), param_names=set(signature.parameters.keys())
    )

    def get_doc_description(name: str) -> str:
        if name in docs:
            return docs[name].description
        return ""

    return {
        name: BaseModelParameter(
            name=name,
            annotation=p.annotation,
            default=p.default,
            doc=get_doc_description(name),
        )
        for name, p in signature.parameters.items()
    }
