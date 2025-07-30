from __future__ import annotations

import inspect
import json
from typing import Any, Callable, Iterable, List, Optional, Tuple, Union

from pydantic import BaseModel, create_model, field_validator

from cotyper.log import log
from cotyper.utils.base_model import create_validator_name


def validate_single(
    model_type: type[BaseModel],
) -> Callable[[type[BaseModel], Any], BaseModel]:
    def inner(cls, obj: model_type | str) -> model_type:
        log.debug(
            f"Validating multiple object of type {model_type.__name__} with value: {obj}"
        )
        if isinstance(obj, str):
            return model_type.model_validate(json.loads(obj))
        else:
            return obj

    return inner


def validate_multiple(
    model_type: type[BaseModel],
) -> Callable[[type[BaseModel], Iterable[BaseModel | Any]], list[BaseModel]]:
    class ValueModel(BaseModel):
        values: list[model_type]

    def inner(cls, objs: Union[Iterable[model_type], str]) -> List[model_type]:
        log.debug(
            f"Validating multiple objects of type {model_type.__name__} with value: {objs} of type {type(objs)}"
        )

        if isinstance(objs, str):
            # when loading the arguments from a config json file they are already wrapped with some brackets,
            # therefore we will remove them if present
            objs = (
                objs
                if not (objs.startswith("[") and objs.endswith("]"))
                else objs[1:-1]
            )

            # this is some kind of hack to validate a list of BaseModels
            value_model = ValueModel.model_validate(
                json.loads('{"values":[' + objs + "]}")
            )

            return value_model.values
        else:
            return list(objs)

    return inner


def parse_json_fields(
    *field_type: Union[
        Tuple[Union[str, List[str]], type[BaseModel]], str, List[str], type[BaseModel]
    ],
) -> Callable[[type[BaseModel]], type[BaseModel]]:
    """
    decorator function to add a dynamic validator to a pydantic BaseModel such that it will parse a json dict string
    to correct type.

    Example usage:
    ```python
    class Bar(BaseModel):
        baz: str

    @parse_json_fields((["bar", "baz"], Bar), ("foobar", Bar))
    class Foo(BaseModel):
        bar: Bar
        baz: Bar
        foobar: List[Bar]

    foo = Foo(bar='{"baz":"baz"}', baz='{"baz":"bar"}', foobar=['{"baz":"foobar"}'])

    ```
    Args:
        *field_type: tuple of the field or fields to apply this validator on and the type of BaseModel which should be casted

    Returns:
        wrapped BaseModel class object
    """
    # allow parse_json_fields("field_name", FieldTypeAnnotation)
    field_type = (
        ((field_type[0], field_type[1]),)
        if (len(field_type) == 2 and isinstance(field_type[0], str))
        else field_type
    )

    def decorator(cls: type[BaseModel]) -> type[BaseModel]:
        parameters = inspect.signature(cls).parameters

        validators = {}

        for fields, klass_type in field_type:
            field, *fields_ = fields if isinstance(fields, list) else [fields]
            annotation = parameters[field].annotation

            validator = (
                validate_single
                if (annotation == klass_type or annotation == Optional[klass_type])
                else validate_multiple
            )

            klass_validator = field_validator(field, *fields_, mode="before")(
                classmethod(validator(klass_type))
            )

            fields_name = "_".join(fields) if isinstance(fields, list) else field
            validator_name = create_validator_name(fields_name, klass_type)
            validators[validator_name] = klass_validator

        return create_model(
            cls.__name__,
            __base__=cls,
            __doc__=cls.__doc__,
            __module__=cls.__module__,
            __validators__=validators,
        )

    return decorator
