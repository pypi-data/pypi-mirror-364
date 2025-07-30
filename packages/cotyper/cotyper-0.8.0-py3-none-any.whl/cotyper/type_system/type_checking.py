import types
from types import NoneType, UnionType
from typing import Any, Literal, Type, Union, get_args, get_origin

from pydantic import BaseModel

TypeAnnotation = Type[Any]

BasicTypes = (str, int, float)


def _get_non_none_args(annotation: TypeAnnotation) -> list:
    """Helper to get type args excluding None/NoneType."""
    return [tp for tp in get_args(annotation) if tp not in (types.NoneType, None)]


def _get_single_type_arg(
    annotation: TypeAnnotation, check_func
) -> TypeAnnotation | None:
    """Helper to get single type argument if check passes and exactly one arg exists."""
    if not check_func(annotation):
        return None

    args = get_args(annotation)
    return args[0] if len(args) == 1 else None


def _get_single_non_none_arg(
    annotation: TypeAnnotation, check_func
) -> TypeAnnotation | None:
    """Helper to get single non-None type argument if check passes."""
    if not check_func(annotation):
        return None

    args = _get_non_none_args(annotation)
    return args[0] if len(args) == 1 else None


def is_tensor_str_type(type_str: str) -> bool:
    """Check if type is tensor or ndarray"""
    return type_str in ("<class 'torch.Tensor'>", "<class 'numpy.ndarray'>")


def is_base_model_subclass(cls: Any) -> bool:
    """Safely check if class is BaseModel subclass"""
    return isinstance(cls, type) and issubclass(cls, BaseModel)


def is_optional_base_model_subclass(annotation: Any) -> bool:
    """Check if annotation is Optional[BaseModel] type."""
    origin = get_origin(annotation)
    args = get_args(annotation)

    return (
        origin in (Union, types.UnionType)
        and types.NoneType in args
        and len(args) == 2
        and any(
            is_base_model_subclass(arg) for arg in args if arg is not types.NoneType
        )
    )


def is_optional_dict(annotation: TypeAnnotation) -> bool:
    """Check if annotation is an Optional[Dict] type."""
    origin = get_origin(annotation)
    args = get_args(annotation)

    return (
        origin in (Union, types.UnionType)
        and types.NoneType in args
        and get_origin(args[0]) is dict
    )


def is_dict(annotation: TypeAnnotation) -> bool:
    """Check if annotation is a Dict type."""
    origin = get_origin(annotation)
    args = get_args(annotation)
    return (
        origin is dict and len(args) == 2 and args[0] in (int, str, float)
    )  # TODO maybe more keys?


def is_list(annotation: TypeAnnotation) -> bool:
    """Check if annotation is a List type."""
    if annotation is list:
        return True
    origin = get_origin(annotation)
    args = get_args(annotation)
    return origin is list and len(args) == 1


def is_basic_type(annotation: TypeAnnotation) -> bool:
    """Check if annotation is a basic type (str, int, float)."""
    return isinstance(annotation, type) and annotation in BasicTypes


def is_list_basic_type(annotation: TypeAnnotation) -> bool:
    """Check if annotation is List[BasicType]."""
    inner_type = _get_single_type_arg(annotation, is_list)
    return inner_type is not None and is_basic_type(inner_type)


def is_optional_list(annotation: TypeAnnotation) -> bool:
    """Check if annotation is Optional[List[...]]."""
    inner_type = _get_single_non_none_arg(annotation, is_optional)
    return inner_type is not None and is_list(inner_type)


def is_optional_list_basic_types(annotation: TypeAnnotation) -> bool:
    """Check if annotation is Optional[List[BasicType]]."""
    # Get the non-None type from Optional
    list_type = _get_single_non_none_arg(annotation, is_optional)
    if list_type is None or not is_list(list_type):
        return False

    # Get the element type from List
    element_type = _get_single_type_arg(list_type, is_list)
    return element_type is not None and is_basic_type(element_type)


def is_optional(annotation: TypeAnnotation) -> bool:
    origin = get_origin(annotation)
    args = get_args(annotation)
    return origin in (UnionType, Union) and NoneType in args


def is_union(annotation: TypeAnnotation) -> bool:
    origin = get_origin(annotation)
    args = get_args(annotation)
    return origin in (UnionType, Union) and NoneType not in args


def is_tuple(annotation: TypeAnnotation) -> bool:
    """Check if annotation is a Tuple type."""
    origin = get_origin(annotation)
    args = get_args(annotation)
    return origin is tuple and len(args) > 0


def is_optional_tuple(annotation: TypeAnnotation) -> bool:
    """Check if annotation is an Optional[Tuple[...]] type."""
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin in (Union, types.UnionType) and types.NoneType in args:
        args = _get_non_none_args(annotation)
        if len(args) == 1 and get_origin(args[0]) is tuple:
            return True
    return False


def is_tuple_union(tp) -> bool:
    if is_union(tp):
        if tuple((filter(lambda t: get_origin(t) is tuple, get_args(tp)))):
            return True
    return False


def is_optional_tuple_union(tp) -> bool:
    if is_optional(tp):
        args = tuple(filter(lambda t: t is not NoneType, get_args(tp)))
        # was union after all
        if len(args) > 1:
            if tuple((filter(lambda t: get_origin(t) is tuple, args))):
                return True
    return False


def is_literal(annotation: TypeAnnotation) -> bool:
    """Check if annotation is a Literal type."""
    return (
        hasattr(annotation, "__origin__")
        and getattr(annotation, "__origin__") is Literal
    ) or annotation is Literal


def is_optional_literal(annotation: TypeAnnotation) -> bool:
    """Check if annotation is an Optional[Literal] type."""
    origin = get_origin(annotation)
    args = get_args(annotation)

    return (
        origin in (UnionType, Union)
        and NoneType in args
        and len(args) == 2
        and any(is_literal(arg) for arg in args if arg is not NoneType)
    )
