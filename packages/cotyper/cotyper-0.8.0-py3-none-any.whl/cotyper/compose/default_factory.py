from typing import Callable, Optional, Union


class _empty:
    """Marker object for Signature.empty and Parameter.empty."""


def serialize_default_factory(
    factory: Optional[Callable] = None,
) -> Union[str, type[_empty]]:
    return (
        ",".join([value.model_dump_json() for value in factory()])
        if factory
        else _empty
    )
