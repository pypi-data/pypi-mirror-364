import inspect
import json
import os.path
from inspect import _ParameterKind
from typing import Annotated, Any, Callable, Dict, Optional, Tuple, Type, Union

import typer
from click import BadParameter, Context, Parameter
from typer.models import OptionInfo

from cotyper.compose.decompile import resolve_func_args
from cotyper.log import LOG_LEVEL, log
from cotyper.utils.dictionary import flatten_dict_by_keys
from cotyper.utils.file_io import load_json


def conf_callback(
    ctx: Context, param: Parameter, value: Optional[str] = None
) -> Optional[str]:
    """
    Typer.Option callback function to load arguments from a file
    and replace the function default values by loaded parameters

    Args:
        ctx: context
        param: callback parameter
        value: path to config file

    Returns:
        value, the path to the config file
    """
    if value is not None:
        try:
            if os.path.isfile(value):
                conf = load_json(value)
            else:
                conf = json.loads(value)

            conf = flatten_dict_by_keys(conf, cat_key="_", level=100)
            ctx.default_map = ctx.default_map or {}  # Initialize the default map
            ctx.default_map.update(conf)  # Merge the config dict into default_map

        except Exception as ex:
            raise BadParameter(str(ex))
    return value


def add_config_file_argument(fn: Callable, config_file_argument_name: str) -> Callable:
    """
    decorator to enable parameter loading by a config file

    Args:
        fn: function to wrap
        config_file_argument_name: name of the argument that should be assigned to the path to the file

    Returns:
        wrapped function
    """

    def wrapped_function(**kwargs):
        kwargs.pop(config_file_argument_name)
        return fn(**kwargs)

    help_str = (
        "Instead of providing all Arguments in the command line you can provide a path to a config file "
        f"in json format using `--{config_file_argument_name.replace('_', '-')} PATH/TO/YOUR/FILE.json`"
    )

    config_file_argument = inspect.Parameter(
        name=config_file_argument_name,
        kind=_ParameterKind.KEYWORD_ONLY,
        default=None,
        annotation=Annotated[
            Optional[str],
            typer.Option(callback=conf_callback, is_eager=True, help=help_str),
        ],
    )

    old_parameters = inspect.signature(fn).parameters

    if config_file_argument_name in old_parameters.keys():
        raise ValueError(
            f"The argument name {config_file_argument_name} should NOT be in the parameters {old_parameters} of {fn}"
        )

    new_parameters = list(old_parameters.values()) + [config_file_argument]

    wrapped_function.__signature__ = inspect.Signature(new_parameters)
    wrapped_function.__name__ = fn.__name__

    return wrapped_function


class App(typer.Typer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.command_wrapper: Dict[str, Tuple[str, str]] = {}

    def command_info(self, name: str) -> Optional[typer.models.CommandInfo]:
        command_info = [info for info in self.registered_commands if info.name == name]
        return command_info[0] if command_info else None

    def group_info(self, name: str) -> [typer.models.TyperInfo]:
        group_info = [info for info in self.registered_groups if info.name == name]
        return group_info[0] if group_info else None

    def register_command_wrapping(self, command: str, wraps: Tuple[str, str]) -> None:
        self.command_wrapper[command] = wraps

    def struct_command(
        self,
        name: Optional[str] = None,
        *,
        cls: Optional[Type[typer.core.TyperCommand]] = None,
        context_settings: Optional[Dict[Any, Any]] = None,
        help: Optional[str] = None,
        epilog: Optional[str] = None,
        short_help: Optional[str] = None,
        options_metavar: str = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool = False,
        # Rich settings
        rich_help_panel: Union[str, None] = typer.models.Default(None),
        add_config_file_option: Optional[str] = None,
        wraps_command: Optional[Tuple[str, str]] = None,
    ) -> Callable[[typer.models.CommandFunctionType], typer.models.CommandFunctionType]:
        """
        Just like a classical `Typer.command` but it will respect the nested `pydantic.dataclass` and will *unfold*
        the argument `foo` to build a new function which will be passed to `Typer`

         Args:
             name: name of the command exposed to the CLI
             cls:
             context_settings:
             help:
             epilog:
             short_help:
             options_metavar:
             add_help_option:
             no_args_is_help:
             hidden:
             deprecated:
             rich_help_panel:
             add_config_file_option: adding an argument that will load a json with all the parameters of the command
                 and replace the default values of the function arguments by the json
            wraps_command: if a command will execute other command it will display the wrapped command help panel as well

         Returns:

        """

        def decorator(fn):
            resolved_args_fn = resolve_func_args(fn)

            if LOG_LEVEL == "DEBUG":
                log.debug(f"command {name} resolved args fn is {resolved_args_fn}")
                log.debug("signature of resolved args fn is:")
                for param_name, param in inspect.signature(
                    resolved_args_fn
                ).parameters.items():
                    log.debug(f"\t{param_name}: {param.annotation} = {param.default}")
                    if isinstance(param.default, OptionInfo):
                        log.debug(
                            f"\t\tOptionInfo: {param.default}, parser:{param.default.parser}, click_type={param.default.click_type}"
                        )

            return self.command(
                name=name,
                cls=cls,
                context_settings=context_settings,
                help=help,
                epilog=epilog,
                short_help=short_help,
                options_metavar=options_metavar,
                add_help_option=add_help_option,
                no_args_is_help=no_args_is_help,
                hidden=hidden,
                deprecated=deprecated,
                rich_help_panel=rich_help_panel,
                add_config_file_option=add_config_file_option,
                wraps_command=wraps_command,
            )(resolved_args_fn)

        return decorator

    def command(
        self,
        name: Optional[str] = None,
        *,
        cls: Optional[Type[typer.core.TyperCommand]] = None,
        context_settings: Optional[Dict[Any, Any]] = None,
        help: Optional[str] = None,
        epilog: Optional[str] = None,
        short_help: Optional[str] = None,
        options_metavar: str = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool = False,
        # Rich settings
        rich_help_panel: Union[str, None] = typer.models.Default(None),
        add_config_file_option: Optional[str] = None,
        wraps_command: Optional[Tuple[str, str]] = None,
    ) -> Callable[[typer.models.CommandFunctionType], typer.models.CommandFunctionType]:
        super_command = super(App, self).command(
            name=name,
            cls=cls,
            context_settings=context_settings,
            help=help,
            epilog=epilog,
            short_help=short_help,
            options_metavar=options_metavar,
            add_help_option=add_help_option,
            no_args_is_help=no_args_is_help,
            hidden=hidden,
            deprecated=deprecated,
            rich_help_panel=rich_help_panel,
        )

        def decorator(fn):
            if add_config_file_option:
                return super_command(
                    add_config_file_argument(
                        fn, config_file_argument_name=add_config_file_option
                    )
                )
            else:
                return super_command(fn)

        if wraps_command is not None and name is not None:
            self.register_command_wrapping(name, wraps_command)
        return decorator
