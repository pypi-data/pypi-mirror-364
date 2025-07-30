import inspect
import types
from collections import defaultdict
from dataclasses import dataclass
from inspect import Parameter as InspectParameter
from inspect import _empty
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    Union,
    _GenericAlias,
    cast,
    get_args,
    get_origin,
)

import click
import typer
from pydantic import BaseModel, ConfigDict, PositiveFloat, PositiveInt, dataclasses
from rich import print as rprint
from typing_extensions import Annotated

from cotyper.compose.default_factory import serialize_default_factory
from cotyper.log import log
from cotyper.methods.doc import getdoc
from cotyper.type_system.custom_click_types import (
    DictParamType,
    FlexibleTupleParamType,
    ListParamType,
    LiteralParamType,
    T,
    TupleParamType,
)
from cotyper.type_system.extract_types import (
    get_choices_from_literal,
    get_list_value_type,
    get_tp_of_optional,
    get_tuple_types,
)
from cotyper.type_system.type_checking import (
    BasicTypes,
    TypeAnnotation,
    is_base_model_subclass,
    is_dict,
    is_list_basic_type,
    is_literal,
    is_optional,
    is_optional_dict,
    is_optional_list_basic_types,
    is_optional_literal,
    is_optional_tuple,
    is_optional_tuple_union,
    is_tensor_str_type,
    is_tuple,
    is_tuple_union,
)
from cotyper.utils.base_model import create_validator_name
from cotyper.utils.tp import (
    get_inner_types,
)

print = rprint


class BaseModelParameter(NamedTuple):
    name: str
    annotation: type[T] | click.ParamType
    default: T = _empty
    doc: str = ""
    parent: Optional[type] = None

    def __eq__(self, other):
        if not isinstance(other, BaseModelParameter):
            return NotImplemented
        return (
            self.name == other.name
            and self.annotation == other.annotation
            and self.default == other.default
            and self.doc == other.doc
            and self.parent == other.parent
        )


def model_schema_repr(inner_type: BaseModel) -> str:
    return ",".join(
        [
            f'"{p.name}":[{getattr(p.annotation, "__name__", str(p.annotation))}]'
            for p in inspect.signature(inner_type).parameters.values()
        ]
    )


@dataclasses.dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class ProcessingContext:
    """Immutable context for parameter processing"""

    object_: Any
    is_function: bool
    base_model_parameters: Dict[str, Any]
    param: inspect.Parameter
    annotation: Any
    origin: Any
    args: tuple
    inner_type: Any
    doc: str

    def __repr__(self):
        return f"<Origin: {self.object_}, name={self.param.name} type={self.annotation} type_origin={self.origin}, args={self.args} inner={self.inner_type}>"


def create_processing_context(
    object_: Any, base_model_parameters: Dict, param: inspect.Parameter
) -> ProcessingContext:
    """Create immutable processing context from parameter"""
    annotation = param.annotation
    origin = get_origin(annotation)
    args = get_args(annotation)
    inner_type = args[0] if args else Any

    # Handle tuple special case
    if annotation is tuple and origin is None:
        origin = tuple
        if (param.default is not param.empty or param.default is None) and isinstance(
            param.default, tuple
        ):
            inner_type = type(param.default[0])
            n = len(param.default)
        else:
            n = 1
        annotation = Tuple[tuple([inner_type] * n)]

    # Get documentation
    bm_param = base_model_parameters.get(param.name)
    doc = bm_param.doc if bm_param else ""

    return ProcessingContext(
        object_=object_,
        is_function=isinstance(object_, types.FunctionType),
        base_model_parameters=base_model_parameters,
        param=param,
        annotation=annotation,
        origin=origin,
        args=args,
        inner_type=inner_type,
        doc=doc,
    )


def create_base_model_param(
    ctx: ProcessingContext, annotation: Any = None, default: Any = None, doc: str = None
) -> BaseModelParameter:
    """Pure function to create BaseModelParameter"""
    return BaseModelParameter(
        name=ctx.param.name,
        annotation=annotation or ctx.annotation,
        default=default if default is not None else ctx.param.default,
        doc=doc or ctx.doc,
        parent=ctx.object_,
    )


def handle_union_basemodel(
    ctx: ProcessingContext,
) -> Optional[Dict[str, BaseModelParameter]]:
    """Handle Union types with BaseModel"""
    if ctx.origin is not Union or not is_base_model_subclass(ctx.inner_type):
        return None

    # Validate BaseModel has required validator
    if not ctx.is_function and issubclass(ctx.object_, BaseModel):
        validator_name = create_validator_name(ctx.param.name, ctx.inner_type)
        if not hasattr(ctx.object_, validator_name):
            raise ValueError(
                f"The class {ctx.object_} should have json validator for {ctx.param.name}. "
                f"Add `@parse_json_fields('{ctx.param.name}',{ctx.inner_type}) to class {ctx.object_}"
            )

    repr_str = "'{" + model_schema_repr(ctx.inner_type) + "}'"
    new_doc = (
        f"({ctx.annotation}, parse argument as json dictionary {repr_str}) {ctx.doc}"
    )

    param = create_base_model_param(ctx, Optional[str], None, new_doc)
    return {ctx.param.name: param}


def handle_literal_optional(
    ctx: ProcessingContext,
) -> Optional[Dict[str, BaseModelParameter]]:
    """Handle Optional Literal types (Union[Literal[...], None])"""
    if ctx.origin is not Union or types.NoneType not in ctx.args:
        return None

    # Check if the non-None type is a Literal
    non_none_args = [arg for arg in ctx.args if arg is not types.NoneType]
    if len(non_none_args) != 1:
        return None

    literal_type = non_none_args[0]
    literal_origin = get_origin(literal_type)

    if literal_origin is not Literal:
        return None

    # Get the literal values
    param = create_base_model_param(ctx, Optional[LiteralParamType(literal_type)])
    return {ctx.param.name: param}


def handle_optional_tensor(
    ctx: ProcessingContext,
) -> Optional[Dict[str, BaseModelParameter]]:
    """Handle Optional tensor/ndarray types"""
    if ctx.origin is not Union or types.NoneType not in ctx.args:
        return None

    if not is_tensor_str_type(str(ctx.inner_type)):
        return None

    log.warning(
        f"{ctx.param.name}: {ctx.annotation} is a tensor or ndarray and will reduce the type "
        f"to Optional[List[float]] to enable click to parse the values, you should ensure that "
        f"the encapsulating BaseModel will validate the value correctly"
    )

    param = create_base_model_param(ctx, Optional[List[float]], None)
    return {ctx.param.name: param}


def handle_optional_tuple_ellipsis(
    ctx: ProcessingContext,
) -> Optional[Dict[str, BaseModelParameter]]:
    """Handle Optional Tuple[...] types with ellipsis"""
    if ctx.origin is not Union or types.NoneType not in ctx.args:
        return None

    # Handle the case where the tuple has an ellipsis
    if len(ctx.args) == 2 and ctx.args[0] is Ellipsis and ctx.args[1] is types.NoneType:
        param = create_base_model_param(ctx, Optional[List[ctx.inner_type]])
        return {ctx.param.name: param}

    return None


def handle_tuple_ellipsis(
    ctx: ProcessingContext,
) -> Optional[Dict[str, BaseModelParameter]]:
    """Handle Tuple[...] types with ellipsis"""
    if ctx.origin is not tuple or Ellipsis not in ctx.args:
        return None

    # Handle the case where the tuple has an ellipsis
    if len(ctx.args) == 1 and ctx.args[0] is Ellipsis:
        param = create_base_model_param(ctx, List[ctx.inner_type])
        return {ctx.param.name: param}

    # If there are multiple types, we cannot handle it here
    return None


def handle_list_basemodel(
    ctx: ProcessingContext,
) -> Optional[Dict[str, BaseModelParameter]]:
    """Handle List[BaseModel] types"""
    log.debug(f"origin is {ctx.origin}")
    if ctx.origin is not list or not is_base_model_subclass(ctx.inner_type):
        return None

    model_signature = "'{" + model_schema_repr(ctx.inner_type) + "}, ...'"
    doc = (
        ctx.doc
        + f" - list of json objects with signature {model_signature} as one string"
    )

    if ctx.is_function:
        param = create_base_model_param(ctx, str, ctx.param.default, doc)
    else:
        if issubclass(ctx.object_, BaseModel):
            serialized_values = serialize_default_factory(
                ctx.object_.model_fields[ctx.param.name].default_factory
            )
            param = create_base_model_param(ctx, str, serialized_values, doc)
        else:
            param = create_base_model_param(ctx, str, ctx.param.default, doc)

    return {ctx.param.name: param}


def handle_list_basic_types(
    ctx: ProcessingContext,
) -> Optional[Dict[str, BaseModelParameter]]:
    """Handle List[BasicTypes]"""
    log.debug(
        f"Handling List[BasicTypes] for {ctx.param.name} with type {ctx.annotation}"
    )

    if not isinstance(ctx.origin, list) or not issubclass(ctx.inner_type, BasicTypes):
        log.debug("\t ... returning None")
        return None

    if ctx.is_function:
        default_value = ctx.param.default
    else:
        if issubclass(ctx.object_, BaseModel):
            default_factory = ctx.object_.model_fields[
                ctx.param.name
            ].default_factory or (lambda: None)
            default_value = default_factory()
        else:
            default_value = ctx.param.default

    param = create_base_model_param(ctx, List[ctx.inner_type], default_value)
    return {ctx.param.name: param}


def handle_list_other(
    ctx: ProcessingContext,
) -> Optional[Dict[str, BaseModelParameter]]:
    """Handle other List types"""
    if not isinstance(ctx.origin, list):
        return None

    param = create_base_model_param(ctx, List[ctx.inner_type])
    return {ctx.param.name: param}


def handle_tensor_annotation(
    ctx: ProcessingContext,
) -> Optional[Dict[str, BaseModelParameter]]:
    """Handle direct tensor/ndarray annotations"""
    if not is_tensor_str_type(str(ctx.annotation)):
        return None

    log.warning(
        f"{ctx.param.name}: {ctx.annotation} is a tensor or ndarray and will reduce the type "
        f"to List[float] to enable click to parse the values, you should ensure that the "
        f"encapsulating BaseModel will validate the value correctly"
    )

    param = create_base_model_param(ctx, List[float], None)
    return {ctx.param.name: param}


def handle_literal_annotation(
    ctx: ProcessingContext,
) -> Optional[Dict[str, BaseModelParameter]]:
    """Handle Literal annotations"""
    log.debug(
        f"Handling Literal annotation for {ctx.param.name} with type {ctx.annotation}"
    )

    if ctx.origin is not Literal:
        return None
    param = create_base_model_param(ctx, LiteralParamType(ctx.annotation))
    return {ctx.param.name: param}


def handle_generic_alias(
    ctx: ProcessingContext,
) -> Optional[Dict[str, BaseModelParameter]]:
    """Handle _GenericAlias types"""
    if not isinstance(ctx.annotation, _GenericAlias):
        return None

    param = create_base_model_param(ctx)
    return {ctx.param.name: param}


def handle_nested_basemodel(
    ctx: ProcessingContext,
) -> Optional[Dict[str, BaseModelParameter]]:
    """Handle nested BaseModel types"""
    if not is_base_model_subclass(ctx.annotation):
        return None

    nested_schema = get_schema(ctx.annotation)
    return {
        f"{ctx.param.name}_{sub_name}": nested_annotation
        for sub_name, nested_annotation in nested_schema.items()
    }


def handle_default_case(ctx: ProcessingContext) -> Dict[str, BaseModelParameter]:
    """Handle default case"""
    param = create_base_model_param(ctx)
    return {ctx.param.name: param}


def process_parameter_with_origin(
    ctx: ProcessingContext,
) -> Optional[Dict[str, BaseModelParameter]]:
    """Process parameters that have an origin (generic types)"""
    if ctx.origin is None:
        return None

    # Chain of responsibility pattern with functional approach
    handlers = [
        handle_union_basemodel,
        handle_literal_optional,
        handle_literal_annotation,
        handle_optional_tensor,
        handle_list_basemodel,
        handle_list_basic_types,
        handle_list_other,
        handle_tuple_ellipsis,
        handle_optional_tuple_ellipsis,
    ]

    log.debug(
        f"Processing parameter with origin: {ctx.param.name} of type {ctx.annotation}"
    )
    for handler in handlers:
        log.debug(f"\t Handler: {handler.__name__}")
        result = handler(ctx)
        if result is not None:
            log.debug(f"\t Handler {handler.__name__} returned: {result}")
            return result

    # Default case for origin-based types
    param = create_base_model_param(ctx)
    return {ctx.param.name: param}


def process_parameter_without_origin(
    ctx: ProcessingContext,
) -> Dict[str, BaseModelParameter]:
    """Process parameters without origin"""
    # Chain of responsibility for non-origin types
    handlers = [
        handle_tensor_annotation,
        handle_generic_alias,
        handle_nested_basemodel,
    ]

    for handler in handlers:
        result = handler(ctx)
        if result is not None:
            return result

    return handle_default_case(ctx)


def process_single_parameter(ctx: ProcessingContext) -> Dict[str, BaseModelParameter]:
    """Process a single parameter and return schema entries"""
    # First try origin-based processing
    if ctx.origin is not None:
        result = process_parameter_with_origin(ctx)
        if result is not None:
            return result

    # Then try non-origin processing
    return process_parameter_without_origin(ctx)


def merge_schemas(
    schema: Dict[str, BaseModelParameter], new_entries: Dict[str, BaseModelParameter]
) -> Dict[str, BaseModelParameter]:
    """Safely merge new entries into schema"""
    result = schema.copy()

    for name, param in new_entries.items():
        if name in result:
            raise ValueError(f"Duplicate parameter name '{name}' found in schema.")
        result[name] = param

    return result


def get_schema(object_: Any) -> Dict[str, BaseModelParameter]:
    """
    Extract schema from object signature using functional programming approach.

    Args:
        object_: Function or class to extract schema from

    Returns:
        Dictionary mapping parameter names to BaseModelParameter objects
    """
    signature = inspect.signature(object_)
    base_model_parameters = getdoc(object_)

    # Create processing contexts for all parameters
    contexts = [
        create_processing_context(object_, base_model_parameters, param)
        for param in signature.parameters.values()
    ]

    # Process each parameter and collect results
    schema_entries = [process_single_parameter(ctx) for ctx in contexts]

    # Merge all schema entries
    final_schema = {}
    for entries in schema_entries:
        final_schema = merge_schemas(final_schema, entries)

    return final_schema


# TODO refactor recompile_basmodel and recompile_arguments such that it removes redundant code repeating


def normalize_string_value(value: Any) -> Any:
    """Normalize string values by replacing single quotes with double quotes."""
    if isinstance(value, str):
        return value.replace("'", '"')
    return value


def extract_direct_parameters(
    signature: inspect.Signature, key_word_arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """Extract parameters that directly match function signature parameters."""
    return {
        param.name: normalize_string_value(key_word_arguments[param.name])
        for param in signature.parameters.values()
        if param.name in key_word_arguments
    }


def extract_complex_parameters(
    signature: inspect.Signature, key_word_arguments: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """Extract parameters that represent nested complex types (prefixed with param_name_)."""
    complex_types: Dict[str, Dict[str, Any]] = defaultdict(dict)

    for param in signature.parameters.values():
        param_prefix = f"{param.name}_"

        for key, value in key_word_arguments.items():
            if key.startswith(param_prefix):
                nested_key = key.replace(param_prefix, "")
                complex_types[param.name][nested_key] = value

    return complex_types


def resolve_complex_parameters(
    signature: inspect.Signature, complex_types: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Resolve complex parameters by recursively recompiling them."""
    resolved = {}

    for param_name, nested_kwargs in complex_types.items():
        param_annotation = signature.parameters[param_name].annotation
        resolved[param_name] = recompile_basemodel(param_annotation, nested_kwargs)

    return resolved


def build_kwargs_from_signature(
    signature: inspect.Signature, key_word_arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """Build complete kwargs by combining direct and complex parameters."""
    direct_params = extract_direct_parameters(signature, key_word_arguments)
    complex_params = extract_complex_parameters(signature, key_word_arguments)
    resolved_complex = resolve_complex_parameters(signature, complex_params)

    return {**direct_params, **resolved_complex}


def recompile_basemodel(
    t: Type[BaseModel], key_word_arguments: Dict[str, Any]
) -> BaseModel:
    """
    Recompile a BaseModel with the given keyword arguments.

    Args:
        t: The BaseModel class to instantiate
        key_word_arguments: Dictionary of arguments, including nested ones with underscore notation

    Returns:
        Instance of the BaseModel class
    """
    signature = inspect.signature(t)
    kwargs = build_kwargs_from_signature(signature, key_word_arguments)
    return t(**kwargs)


def recompile_arguments(
    key_word_arguments: Dict[str, Any], fn: Callable
) -> Dict[str, Any]:
    """
    Recompile arguments for a function by resolving nested BaseModel parameters.

    Args:
        key_word_arguments: Dictionary of arguments, including nested ones with underscore notation
        fn: The function whose signature to match

    Returns:
        Dictionary of resolved arguments ready for function call
    """
    signature = inspect.signature(fn)
    return build_kwargs_from_signature(signature, key_word_arguments)


def unrestr_type(annotation: type) -> type:
    if annotation == PositiveInt:
        return int
    elif annotation == PositiveFloat:
        return float
    else:
        return annotation


def parse_list_basic_types(annotation: type[List[T]]) -> Callable[[List[str]], List[T]]:
    args = get_args(annotation)
    inner_type = args[0] if args else Any

    def inner(list_: List[str]) -> List[T]:
        if (len(list_) == 1 and isinstance(list_[0], str)) or isinstance(list_, str):
            return [inner_type(obj) for obj in list_[0].split(",")]
        else:
            return list_

    return inner


def get_panel_name(name: str, length: int = 1) -> Optional[str]:
    sub = name.split("_")
    return " ".join(sub[:length]).title() if len(sub) > length else None


ParameterSchema = Dict[str, Any]  # Replace with actual schema type
ClickParser = Any


@dataclass(frozen=True)
class ParameterConfig:
    """Immutable configuration for a parameter."""

    name: str
    annotation: TypeAnnotation
    doc: str
    default: Any
    callback: Optional[Callable] = None
    parser: Optional[ClickParser] = None
    click_type: Optional[click.ParamType] = None
    rich_help_panel: Optional[str] = None

    def __post_init__(self):
        log.debug(
            f"<ParameterConfig({self.name}, {self.annotation}, {self.click_type}, {self.callback}, {self.parser}>"
        )


@dataclass(frozen=True)
class TypeProcessingResult:
    """Result of type processing with all necessary information."""

    annotation: TypeAnnotation
    callback: Optional[Callable] = None
    parser: Optional[Callable[[str], TypeAnnotation]] = None
    click_type: Optional[click.ParamType] = None
    doc_suffix: str = ""


# Type processors - each handles a specific type pattern


def process_list_basic_type(annotation: TypeAnnotation) -> TypeProcessingResult:
    """Process list of basic types."""
    log.debug(f"Processing list basic type: {annotation}")

    additional_doc = f"({annotation} use `,` separated arguments)"
    maybe_optional = is_optional(annotation)
    tp = get_list_value_type(annotation)
    return TypeProcessingResult(
        annotation=List[str],
        click_type=ListParamType(value_type=tp, is_optional=maybe_optional),
        doc_suffix=additional_doc,
    )


def process_tuple_union_type(annotation: TypeAnnotation) -> TypeProcessingResult:
    """Process tuple union types."""
    is_ellipsis = any(tp is Ellipsis for tp in get_inner_types(annotation))
    annotation_is_optional = is_optional(annotation)
    args = get_args(annotation)

    # Case 1: Union of tuple types (Tuple[Ta] | Tuple[Tb])
    if all(get_origin(arg) is tuple for arg in args):
        click_type = _process_tuple_union(args, annotation_is_optional)
    else:
        # Case 2: Regular tuple union
        click_type = _process_regular_tuple_union(
            annotation, is_ellipsis, annotation_is_optional
        )

    # Build result annotation
    processed_annotation = Any | None if annotation_is_optional else Any

    return TypeProcessingResult(
        annotation=processed_annotation,
        click_type=click_type,
        doc_suffix=" (use a comma separated list for tuple input)",
    )


def _process_tuple_union(args: tuple, is_optional: bool) -> FlexibleTupleParamType:
    """Handle union of tuple types like Tuple[Ta] | Tuple[Tb]."""
    # Filter out None types for optional handling
    tuples = [arg for arg in args if arg not in (None, types.NoneType)]
    inner_types = [get_args(t) for t in tuples]

    # Validate all tuples have same length
    if not inner_types or not all(
        len(inner) == len(inner_types[0]) for inner in inner_types[1:]
    ):
        raise TypeError("Tuple length mismatch")

    # Validate all positions have same type across tuples
    if not all(len(set(inner)) == 1 for inner in inner_types):
        raise TypeError("Tuple with multiple types not supported")

    size = len(inner_types[0])
    element_types = {inner[0] for inner in inner_types}

    return FlexibleTupleParamType(element_types, size=size, is_optional=is_optional)


def _process_regular_tuple_union(
    annotation: TypeAnnotation, is_ellipsis: bool, is_optional: bool
) -> FlexibleTupleParamType:
    """Handle regular tuple union types."""
    inner_types = [
        tp
        for tp in get_inner_types(annotation)
        if tp not in (None, types.NoneType, Ellipsis)
    ]

    # Validate type consistency (allow int/float mix or single type)
    unique_types = set(inner_types)
    if unique_types != {int, float} and len(unique_types) > 1:
        raise TypeError(
            f"All inner types of a tuple union should be the same type but got {annotation}"
        )

    # Calculate size
    size = None if is_ellipsis else len(inner_types) - 1
    if size is not None and size < 1:
        raise TypeError(
            f"Tuple union type {annotation} should have at least one element, but got {size}"
        )

    return FlexibleTupleParamType(inner_types[0], size=size, is_optional=is_optional)


def process_literal_click_param_type(
    annotation: TypeAnnotation,
) -> TypeProcessingResult:
    """Process LiteralChoice types."""
    _is_optional_literal = is_optional(annotation)

    if _is_optional_literal:
        literal_choice = get_args(annotation)[0]
        literal_choice = cast(LiteralParamType, literal_choice)
        click_param = literal_choice
        result_annotation = Optional[type(literal_choice.choices[0])]
    else:
        click_param = annotation
        if not _is_optional_literal:
            annotation = cast(LiteralParamType, annotation)
        result_annotation = type(annotation.choices[0])

    choices_str = "| ".join([f"'{choice}'" for choice in click_param.choices])
    doc_suffix = f"Use one of the following choices: {{{choices_str}}}"
    return TypeProcessingResult(
        annotation=result_annotation, click_type=click_param, doc_suffix=doc_suffix
    )


def process_dict_type(
    annotation: TypeAnnotation, _optional: bool = False
) -> TypeProcessingResult:
    """Process Dict types."""

    if _optional:
        # If it's an Optional[Dict], we need to handle None case
        if get_origin(annotation) is Union and types.NoneType in get_args(annotation):
            key_type, value_type = get_args(annotation)[0].__args__

            return TypeProcessingResult(
                annotation=Optional[Dict[key_type, value_type]],
                click_type=DictParamType(key_type, value_type, is_optional=True),
                doc_suffix=" (use JSON string or file for dict input)",
            )
    else:
        # If it's a Dict, we assume it has two arguments: key_type and value_type
        key_type, value_type = get_args(annotation)
        if not (key_type and value_type):
            raise TypeError(
                f"Dict type annotation {annotation} must have two type arguments."
            )

    return TypeProcessingResult(
        annotation=annotation,
        click_type=DictParamType(key_type=key_type, value_type=value_type),
        doc_suffix=" (use JSON string or file for dict input)",
    )


def process_default_type(annotation: TypeAnnotation) -> TypeProcessingResult:
    """Process default/standard types."""
    return TypeProcessingResult(annotation=annotation)


def process_optional_dict(annotation: TypeAnnotation) -> TypeProcessingResult:
    return process_dict_type(annotation, _optional=True)


def process_dict(annotation: TypeAnnotation) -> TypeProcessingResult:
    return process_dict_type(annotation, _optional=False)


def process_tuple_type(annotation: TypeAnnotation) -> TypeProcessingResult:
    maybe_optional = is_optional(annotation)
    tuple_types = get_tuple_types(cast(Type[tuple], annotation))
    return TypeProcessingResult(
        annotation=annotation,
        click_type=TupleParamType(list(tuple_types), is_optional=maybe_optional),
        doc_suffix=" (use a comma separated list for tuple input)",
    )


def process_literal_type(annotation: TypeAnnotation) -> TypeProcessingResult:
    maybe_optional = is_optional_literal(annotation)

    literal_type = get_tp_of_optional(annotation) if maybe_optional else annotation
    choices = get_choices_from_literal(literal_type)
    choices_str = "| ".join(f'"{choice}"' for choice in choices)
    return TypeProcessingResult(
        annotation=annotation,
        click_type=LiteralParamType(
            literal_type=literal_type, is_optional=maybe_optional
        ),
        doc_suffix=f" (select one of [{choices_str}])",
    )


def is_literal_param_type(annotation: TypeAnnotation) -> bool:
    """Check if annotation is a LiteralParamType."""
    return isinstance(annotation, LiteralParamType)


def is_optional_literal_param_type(annotation: TypeAnnotation) -> bool:
    return is_optional(annotation) and isinstance(
        get_args(annotation)[0], LiteralParamType
    )


def is_dict_with_literals(annotation: TypeAnnotation) -> bool:
    """Check if annotation is a dict type with literal key and value types."""
    origin = get_origin(annotation)
    if origin not in (dict, Dict):
        return False

    args = get_args(annotation)

    # Handle optional types by filtering out None/NoneType
    if is_optional(annotation):
        args = [arg for arg in args if arg is not None and arg is not types.NoneType]

    # Dict must have exactly 2 type arguments (key, value)
    if len(args) != 2:
        return False

    key_tp, value_tp = args
    return is_literal(key_tp) and is_literal(value_tp)


def is_optional_dict_with_literals(annotation: TypeAnnotation) -> bool:
    return is_dict_with_literals(annotation) and is_optional(annotation)


# Type processing strategy - maps type patterns to processors
# - lists
#   - List[BasicType]
#   - Optional[List[BasicType]]
# - tuples
#   - Tuple[T, ...]
#   - Optional[Tuple[T, ...]]
# - flexible tuples, tuple or scalar
#   - Union[Tuple[T, ...], T]
#   - Optional[Union[Tuple[T, ...], T]]
# - literals
#   - Literal[...]
#   - Optional[Literal[...]]
# - dicts
#   - Dict[K, V]
#   - Optional[Dict[K, V]]
TYPE_PROCESSORS = [
    (is_list_basic_type, process_list_basic_type),
    (is_optional_list_basic_types, process_list_basic_type),
    (is_tuple, process_tuple_type),
    (is_optional_tuple, process_tuple_type),
    (is_tuple_union, process_tuple_union_type),
    (is_optional_tuple_union, process_tuple_union_type),
    (is_literal, process_literal_type),
    (is_optional_literal, process_literal_type),
    (is_dict, process_dict),
    (is_optional_dict, process_optional_dict),
    (is_literal_param_type, process_literal_click_param_type),
    (is_optional_literal_param_type, process_literal_click_param_type),
    (is_dict_with_literals, process_dict_type),
    (is_optional_dict_with_literals, process_dict_type),
]


def process_type_annotation(annotation: TypeAnnotation) -> TypeProcessingResult:
    """
    Process type annotation using strategy pattern.
    Returns the first matching processor result or default processing.
    """

    log.debug(f"🔎 Processing type annotation: {annotation}")
    for predicate, processor in TYPE_PROCESSORS:
        log.debug(f"\tTesting predicate: {predicate.__name__}")
        if predicate(annotation):
            log.debug(f"\t➡️  Matched processor: {processor.__name__}")
            return processor(annotation)
    log.debug(f"No processor matched for {annotation}, using default processing.")
    return process_default_type(annotation)


def create_parameter_config(name: str, param: Any) -> ParameterConfig:
    """Create parameter configuration from schema parameter."""
    annotation = unrestr_type(param.annotation)
    doc = param.doc
    rich_help_panel = get_panel_name(name)

    type_result = process_type_annotation(annotation)

    return ParameterConfig(
        name=name,
        annotation=type_result.annotation,
        doc=doc + type_result.doc_suffix,
        default=param.default,
        callback=type_result.callback,
        parser=type_result.parser,
        click_type=type_result.click_type,
        rich_help_panel=rich_help_panel,
    )


def create_typer_option(config: ParameterConfig) -> typer.Option:
    """Create typer.Option from parameter configuration."""
    return typer.Option(
        config.default if config.default is not _empty else ...,
        help=config.doc,
        callback=config.callback,
        rich_help_panel=config.rich_help_panel,
        parser=config.parser,
        click_type=config.click_type,
    )


def maybe_make_none_type(
    annotation: TypeAnnotation, click_type: click.ParamType | None = None
) -> TypeAnnotation | Any:
    log.debug(f"Maybe making None type for {annotation} with click type {click_type}")

    if click_type is not None and isinstance(
        click_type,
        (
            FlexibleTupleParamType,
            LiteralParamType,
            ListParamType,
            TupleParamType,
            DictParamType,
        ),
    ):
        new_annotation = Any
    else:
        new_annotation = annotation

    log.debug(f"New annotation is {new_annotation}")
    return new_annotation


def create_inspect_parameter(config: ParameterConfig) -> InspectParameter:
    """Create inspect.Parameter from parameter configuration."""
    log.debug(
        f"Creating inspect parameter for {config.name} with type {config.annotation} with click type {config.click_type}"
    )

    return InspectParameter(
        name=config.name,
        kind=InspectParameter.KEYWORD_ONLY,
        default=create_typer_option(config),
        annotation=maybe_make_none_type(config.annotation, config.click_type),
    )


def create_function_annotations(parameters: List[ParameterConfig]) -> Dict[str, Any]:
    """Create function annotations dictionary."""

    function_annotation = {
        param.name: Annotated[
            maybe_make_none_type(unrestr_type(param.annotation), param.click_type),
            typer.Argument(
                (param.default if param.default is not _empty else ...), help=param.doc
            ),
        ]
        for param in parameters
    }
    log.debug(f"Function annotations created: {function_annotation}")
    return function_annotation


def create_wrapped_function(original_fn: Callable) -> Callable:
    """Create the wrapped function that recompiles arguments."""

    def new_func(**kwargs):
        new_kwargs = recompile_arguments(kwargs, original_fn)
        return original_fn(**new_kwargs)

    return new_func


def resolve_func_args(fn: Callable) -> Callable:
    """
    Resolve complex or pydantic function arguments into flat descriptive arguments.

    This function transforms a function with deeply nested complex struct-like arguments
    into one with a flat hierarchy that Typer can handle. The flat arguments are
    re-compiled to their complex structs when the function is called.

    Args:
        fn: Function with deeply nested complex struct-like arguments

    Returns:
        Function with flat hierarchy function args which will be re-compiled when called
    """
    log.debug(f"Resolving function arguments for {fn.__name__}")
    schema = get_schema(fn)

    # Create parameter configurations
    param_configs = [
        create_parameter_config(name, param) for name, param in schema.items()
    ]

    # Create inspect parameters
    parameters = [create_inspect_parameter(config) for config in param_configs]

    # Create the new function
    new_func = create_wrapped_function(fn)

    # Set function metadata
    new_func.__signature__ = inspect.Signature(parameters)
    new_func.__annotations__ = create_function_annotations(param_configs)
    new_func.__name__ = fn.__name__

    return new_func


# Extension point: Adding new type processors
def register_type_processor(
    predicate: Callable[[TypeAnnotation], bool],
    processor: Callable[[TypeAnnotation], TypeProcessingResult],
) -> None:
    """
    Register a new type processor for custom types.

    Args:
        predicate: Function that returns True if the processor should handle this type
        processor: Function that processes the type and returns TypeProcessingResult
    """
    TYPE_PROCESSORS.insert(
        0, (predicate, processor)
    )  # Insert at beginning for priority
