import inspect
from collections import defaultdict
from copy import deepcopy
from typing import Any, Callable, Dict, get_args, get_origin

from pydantic import BaseModel

from cotyper.compose.default_factory import serialize_default_factory
from cotyper.utils.base_model import replace


def fold_cls(
    *cls: type, remapping_keys: Dict[type, str], **kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    kwargs_cp = deepcopy(kwargs)

    cls_parameters = {c: list(inspect.signature(c).parameters.values()) for c in cls}

    name_type_mapping = {
        param.name: klass
        for klass, parameters in cls_parameters.items()
        for param in parameters
    }

    klass_kwargs = defaultdict(dict)

    for key, value in kwargs.items():
        klass = name_type_mapping.get(key, None)
        if klass is not None:
            klass_kwargs[klass][key] = value
            kwargs_cp.pop(key)

    # update copied kwargs with folded classes
    return {
        **kwargs_cp,
        **{remapping_keys[klass]: klass(**kw) for klass, kw in klass_kwargs.items()},
    }


def make_kw_only(parameter: inspect.Parameter) -> inspect.Parameter:
    return inspect.Parameter(
        name=parameter.name,
        kind=inspect._ParameterKind.KEYWORD_ONLY,
        default=parameter.default,
        annotation=parameter.annotation,
    )


def unfold_cls(*cls: type) -> Callable:
    def decorator(fn):
        cls_parameters = {
            c: {
                key: parameter
                for key, parameter in inspect.signature(c).parameters.items()
            }
            for c in cls
        }

        unfolded_func_parameters: Dict[str, inspect.Parameter] = {}
        signature = inspect.signature(fn)
        fn_arg_ames = set(signature.parameters.keys())
        remapping_keys = {}
        for key, function_parameter in signature.parameters.items():
            cls_parameter = cls_parameters.get(function_parameter.annotation, None)

            if cls_parameter is not None:
                remapping_keys[function_parameter.annotation] = key

                for cls_key, param in cls_parameter.items():
                    if cls_key in fn_arg_ames or cls_key in unfolded_func_parameters:
                        raise ValueError(
                            f"Unfolding class {function_parameter.annotation} with parameter {param}"
                            f" conflicts with existing function argument {signature.parameters[cls_key] if cls_key in fn_arg_ames else unfolded_func_parameters[cls_key]}"
                        )

                    origin = get_origin(param.annotation)
                    args = get_args(param.annotation)
                    inner_type = args[0] if args else Any

                    default_factory = function_parameter.annotation.model_fields[
                        param.name
                    ].default_factory

                    if isinstance(origin, list) and issubclass(inner_type, BaseModel):
                        default = serialize_default_factory(default_factory)
                    elif isinstance(origin, list) and default_factory is not None:
                        default = default_factory()
                    else:
                        default = param.default

                    new_param = replace(
                        param, kind=inspect._ParameterKind.KEYWORD_ONLY, default=default
                    )
                    unfolded_func_parameters[cls_key] = new_param
            else:
                unfolded_func_parameters[key] = make_kw_only(function_parameter)

        def unfolded_function(**kwargs):
            folded_kwargs = fold_cls(*cls, remapping_keys=remapping_keys, **kwargs)
            return fn(**folded_kwargs)

        unfolded_function.__name__ = fn.__name__
        unfolded_function.__signature__ = inspect.Signature(
            list(unfolded_func_parameters.values())
        )

        unfolded_function.__annotations__ = {
            name: param.annotation for name, param in unfolded_func_parameters.items()
        }

        return unfolded_function

    return decorator
