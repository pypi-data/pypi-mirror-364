from typing import (
    Dict,
    Literal,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from cotyper.type_system.type_checking import (
    _get_non_none_args,
    is_literal,
    is_optional,
)

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def get_tp_of_optional(annotation: Type[Optional[T]]) -> Type[T]:
    """Extract the type from an Optional type annotation."""
    if is_optional(annotation):
        args = _get_non_none_args(annotation)
        if len(args) == 1:
            return args[0]
    raise ValueError(f"Unsupported annotation type: {annotation}")


def get_choices_from_literal(
    annotation: Union[Type[Literal[T]], Type[Optional[Literal[T]]]],
) -> set[T]:
    """Extract choices from a Literal type annotation."""
    if is_literal(annotation):
        return set(get_args(annotation))
    elif is_optional(annotation):
        inner_args = get_args(annotation)
        for arg in inner_args:
            if is_literal(arg):
                return set(get_args(arg))
    return set()


def get_key_value_type_from_dict(
    annotation: Union[Type[Dict[K, V]], Type[Optional[Dict[K, V]]]],
) -> tuple[Type[K], Type[V]]:
    """Extract key and value types from a Dict type annotation."""
    if is_optional(annotation):
        inner_args = get_args(annotation)
        for arg in inner_args:
            if get_origin(arg) in (dict, Dict):
                args = get_args(arg)
                if len(args) == 2:
                    return args[0], args[1]

    elif get_origin(annotation) in (dict, Dict):
        args = get_args(annotation)
        if len(args) == 2:
            return args[0], args[1]

    raise ValueError(f"Unsupported annotation type: {annotation}")


def get_list_value_type(annotation: Type[Union[list[T], Optional[list[T]]]]) -> Type[T]:
    """Extract the value type from a List type annotation."""
    if is_optional(annotation):
        inner_args = get_args(annotation)
        for arg in inner_args:
            if get_origin(arg) is list:
                args = get_args(arg)
                if args:
                    return args[0]
    elif get_origin(annotation) is list:
        args = get_args(annotation)
        if args:
            return args[0]

    raise ValueError(f"Unsupported annotation type: {annotation}")


def get_union_types(
    annotation: Union[Type[Union[T, ...]], Type[Optional[Union[T, ...]]]],
) -> tuple[Type[T], ...]:
    """Extract types from a Union type annotation."""
    if is_optional(annotation):
        return tuple(_get_non_none_args(annotation))
    elif get_origin(annotation) is Union:
        return get_args(annotation)

    raise ValueError(f"Unsupported annotation type: {annotation}")


def get_tuple_types(annotation: Type[tuple[T, ...]]) -> Tuple[Type[T], ...]:
    """Extract types from a Tuple type annotation."""
    if get_origin(annotation) is tuple:
        return get_args(annotation)
    elif is_optional(annotation):
        inner_args = get_args(annotation)
        for arg in inner_args:
            if get_origin(arg) is tuple:
                return get_args(arg)

    raise ValueError(f"Unsupported annotation type: {annotation}")


def get_flexible_tuple_types(annotation: Type) -> Type[T]:
    """
    Extracts the inner type T from a flexible annotation like:
    - Union[Tuple[T, T], T]
    - Optional[Union[Tuple[T, T], T]]
    Returns the single consistent type T, or raises ValueError if not possible.
    """
    typs: Set[Type[T]] = set()

    args = get_args(annotation)

    # Unwrap Optional[...] (i.e., Union[..., None])
    if is_optional(annotation):
        args = _get_non_none_args(annotation)

    # If it's not a Union at this point, make it look like one
    if get_origin(annotation) is not Union:
        args = (annotation,)

    for arg in args:
        if get_origin(arg) is tuple:
            typs.update(get_args(arg))
        else:
            typs.add(arg)

    if len(typs) == 1:
        return typs.pop()

    raise ValueError(f"Expected exactly one consistent inner type, got: {typs}")


def get_tuple_size(annotation: Type[tuple[T, ...]]) -> int:
    """Get the size of a Tuple type annotation."""
    if get_origin(annotation) is tuple:
        return len(get_args(annotation))
    elif is_optional(annotation):
        inner_args = get_args(annotation)
        for arg in inner_args:
            if get_origin(arg) is tuple:
                return len(get_args(arg))

    raise ValueError(f"Unsupported annotation type: {annotation}")


def get_flexible_tuple_size(annotation: Type) -> int:
    """
    Extracts the size of a flexible tuple type annotation like:
    - Union[Tuple[T, T], T]
    - Optional[Union[Tuple[T, T], T]]
    Returns the size of the tuple, or raises ValueError if not possible.
    """
    args = get_args(annotation)

    # Unwrap Optional[...] (i.e., Union[..., None])
    if is_optional(annotation):
        args = _get_non_none_args(annotation)

    # If it's not a Union at this point, make it look like one
    if get_origin(annotation) is not Union:
        args = (annotation,)

    for arg in args:
        if get_origin(arg) is tuple:
            return len(get_args(arg))

    raise ValueError(f"Expected a tuple type, got: {annotation}")
