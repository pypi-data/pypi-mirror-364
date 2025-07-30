from enum import Enum
from types import NoneType, UnionType
from typing import Any, Optional, Tuple, Type, Union, get_args, get_origin

from cotyper.type_system.type_checking import (
    is_optional_tuple_union,
    is_tuple_union,
)


def get_inner_types(annotation: Type[Any]) -> Tuple[Type[Any] | Any, ...]:
    # Get origin (like list, Union, etc.) and arguments
    origin = get_origin(annotation)
    args = get_args(annotation)
    if not origin and isinstance(annotation, str):
        return (annotation,)
    # Handle simple case - it's an Enum
    if not origin and issubclass(annotation, Enum):
        return (annotation,)

    # Handle Union, list, tuple types
    if origin in (UnionType, Union, list, tuple):
        inner = []

        # Process each argument recursively
        for arg in args:
            arg_origin = get_origin(arg)

            if arg_origin:
                # Recursively process nested structures
                if arg_origin in (UnionType, Union, list, tuple):
                    inner.extend(get_inner_types(arg))
                else:
                    raise ValueError(f"Unsupported type structure: {arg_origin}")
            elif arg not in (None, NoneType):
                # Skip None types, add concrete types
                inner.append(arg)

        return tuple(inner)


if __name__ == "__main__":
    optional_tp = Optional[Tuple[int, int] | int]
    tp = Tuple[int, int] | int

    assert is_tuple_union(tp)
    assert is_optional_tuple_union(optional_tp), f"{optional_tp} is false"
