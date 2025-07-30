import inspect
from typing import TypeVar

from cotyper.utils.string import model_name_to_snake

T = TypeVar("T")


def replace(obj: T, **kw) -> T:
    """
    Creates a new object with arguments that are exposed in the signature of type[T] and accessible
    while updating the arguments given in `**kw`. All arguments from the signature should be accessible as property
    Args:
        obj: instance to update respectively replace some arguments
        **kw: key word arguments to replace attributes in `obj`. Key word arguments must be exposed in the signature
            of the object

    Returns:
        new instance of the object with updated arguments
    """
    parameter_names = inspect.signature(type(obj)).parameters.keys()
    arguments = {}

    for name in parameter_names:
        if not hasattr(obj, name):
            raise ValueError(
                f"The obj {type(obj)} should have all __init__ values as attributes. "
                f"The parameter {name} is not an attribute of {type(obj)}"
            )
        arguments[name] = getattr(obj, name)

    arguments.update(kw)
    return type(obj)(**arguments)


def create_validator_name(fields_name: str, klass_type: T):
    return f"parse_{fields_name}_{model_name_to_snake(klass_type)}"
