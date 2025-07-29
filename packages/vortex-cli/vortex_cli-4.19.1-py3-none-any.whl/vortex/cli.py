from __future__ import annotations

import functools
from argparse import ArgumentParser
from argparse import ArgumentTypeError
from argparse import Namespace
from argparse import RawDescriptionHelpFormatter
from argparse import _ArgumentGroup
from argparse import _MutuallyExclusiveGroup
from argparse import _SubParsersAction
from pathlib import Path

from vortex.models import DesignType

_EXECUTE_PARSER_DESCRIPTION = """\
    status                | Display the server status
    sessions              | Display the user sessions
    session [username]    | Display the session details
    quit [save]           | Shut down the server, opt. save sessions
    gc                    | Ask the JVM to collect garbage
    restart server [save] | Restart the server, reloading puakma.jar, opt. save sessions
    load [class]          | Load the named class ie: 'puakma.addin.http.HTTP'
    unload [task]         | Unload the named task ie: HTTP
    reload [task]         | Unload then load the named task ie: HTTP
    drop [who]            | Drop user session. Use 'all' for all sessions
    tell TASK ...         | Tells a task to perform some action
    clear ITEM            | eg: log, errors
    config WHAT           | Use RELOAD to refresh the server settings
    show VARNAME          | Shows a puakma.config variable, or java for System props
    stats                 | Display statistics from each server addin
    store WHAT            | Access the global cache; flush, status
"""


def _check_int_in_range(val: str, min_: int = 0, max_: int | None = 50) -> int:
    new_val = int(val)
    if new_val < min_ or (max_ is not None and new_val > max_):
        raise ArgumentTypeError(f"%s is not between {min_} and {max_}. " % val)
    return new_val


def _pmx_type(val: str) -> Path:
    path = Path(val).resolve()
    if path.suffix != ".pmx" or not path.is_file():
        raise ArgumentTypeError(f"Invalid '.pmx' file {path}")
    return path


def _non_empty_string(val: str) -> str:
    if not val.strip():
        raise ArgumentTypeError("Value provided cannot be empty or just whitespace.")
    return val


def _add_server_option(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--server",
        "-s",
        metavar="NAME",
        help="The name of the server definition in the config file to use",
    )


def _add_design_type_option(
    parser: ArgumentParser | _MutuallyExclusiveGroup | _ArgumentGroup,
    nargs: str | None = "*",
    required: bool = False,
    help_suffix: str | None = None,
) -> None:
    parser.add_argument(
        "--type",
        "-t",
        nargs=nargs,
        required=required,
        dest="design_type",
        type=DesignType.from_name,
        metavar="DESIGN_TYPE",
        help=(
            f"Choices: {[t.name.lower() for t in DesignType if t != DesignType.ERROR]}"
            f"{help_suffix or ''}"
        ),
    )


def validate_args(
    args: Namespace,
    new_parser: ArgumentParser,
    clone_parser: ArgumentParser,
    db_parser: ArgumentParser,
) -> None:
    if args.command == "new":
        msg = None
        is_update_mode = bool(args.update_ids)
        if args.subcommand == "object":
            missing_required_fields = not is_update_mode and not (
                args.name and args.app_id and args.design_type
            )
            missing_content_type = (
                args.design_type in (DesignType.RESOURCE, DesignType.DOCUMENTATION)
                and not args.content_type
            )
            update_arg_contains_app_id = is_update_mode and args.app_id
            update_is_missing_args = is_update_mode and not (
                args.name
                or args.app_id
                or args.design_type
                or args.comment
                or args.inherit_from
                or args.open_action
                or args.save_action
                or args.parent_page
                or args.content_type
            )
            if missing_required_fields:
                msg = "--name, --app-id, and --type are required unless using --update"
            elif missing_content_type:
                msg = (
                    f"--type argument value '{args.design_type.name}' "
                    "requires --content-type"
                )
            elif update_arg_contains_app_id:
                msg = "Can't use --app-id with --update"
            elif update_is_missing_args:
                msg = "Please specify an option to update"
        elif args.subcommand == "app":
            if not is_update_mode and not (args.name and args.group):
                msg = "--name and --group are required when creating new applications."
        if msg:
            new_parser.error(msg)

    elif args.command == "clone" and not (args.app_ids or args.reclone):
        clone_parser.error("Please specifiy the APP_ID[s] to clone or use '--reclone'")
    elif args.command == "db" and args.sql is not None:
        try:
            args.database = int(args.database)
        except ValueError:
            db_parser.error(
                "Positional argument 'database' must be a database connection "
                "ID (int) when using the '--sql' option"
            )


def add_code_parser(
    command_parser: _SubParsersAction[ArgumentParser],
) -> ArgumentParser:
    code_parser = command_parser.add_parser(
        "code",
        help="Open the workspace in Visual Studio Code",
        add_help=False,
    )
    code_parser.add_argument("--help", "-h", action="store_true")
    return code_parser


def add_list_parser(command_parser: _SubParsersAction[ArgumentParser]) -> None:
    list_parser = command_parser.add_parser(
        "list",
        aliases=("ls",),
        help=(
            "List Puakma Applications on the server or cloned locally."
            "(ls is an alias for 'vortex list --local')"
        ),
    )
    list_parser.add_argument(
        "--group",
        "-g",
        nargs="*",
        help="Enter application 'group' to filter the results",
    )
    list_parser.add_argument(
        "--name",
        "-n",
        nargs="*",
        help="Enter application 'name' to filter the results",
    )
    list_parser.add_argument(
        "--template",
        "-t",
        nargs="*",
        help="Enter application 'template' to filter the results",
    )
    list_parser.add_argument(
        "--strict",
        help="Strict search when using filters",
        action="store_true",
    )
    list_parser.add_argument(
        "--local",
        action="store_true",
        dest="show_local_only",
        help="List locally cloned applications instead",
    )
    list_parser.add_argument(
        "--show-inherited",
        help="Also display inherited applications",
        action="store_true",
    )
    list_parser.add_argument(
        "--show-inactive",
        help="Also display inactive applications",
        action="store_true",
    )
    list_parser.add_argument(
        "--all",
        "-a",
        help="Show all applications",
        action="store_true",
    )
    list_parser.add_argument(
        "--ids-only",
        "-x",
        help="Show application ID's only",
        dest="show_ids_only",
        action="store_true",
    )
    list_parser.add_argument(
        "--open-urls",
        "-o",
        help="Open each application URL in a web browser",
        action="store_true",
    )
    list_parser.add_argument(
        "--open-dev-urls",
        "-d",
        help="Open each application webdesign URL in a web browser",
        action="store_true",
    )
    list_parser.add_argument(
        "--connections",
        help="List the Database Connections of locally cloned apps",
        action="store_true",
        dest="show_connections",
    )
    _add_server_option(list_parser)


def add_clone_parser(
    command_parser: _SubParsersAction[ArgumentParser],
) -> ArgumentParser:
    clone_parser = command_parser.add_parser(
        "clone",
        help="Clone Puakma Applications and their design objects into the workspace",
    )
    clone_parser.add_argument(
        "app_ids",
        nargs="*",
        metavar="APP_ID",
        help="The ID(s) of the Puakma Application(s) to clone",
        type=int,
    )
    clone_parser.add_argument(
        "--reclone",
        help="Reclone locally cloned applictions",
        action="store_true",
    )
    clone_parser.add_argument(
        "--get-resources",
        "-r",
        help="Also clone application resources",
        action="store_true",
    )
    clone_parser.add_argument(
        "--open-urls",
        "-o",
        help="Open the application and webdesign URLs after cloning",
        action="store_true",
    )
    _add_server_option(clone_parser)
    return clone_parser


def add_export_parser(
    command_parser: _SubParsersAction[ArgumentParser],
) -> ArgumentParser:
    export_parser = command_parser.add_parser(
        "export",
        help="Export Puakma Applications as a .pmx file",
    )
    export_parser.add_argument(
        "app_ids",
        nargs="+",
        metavar="APP_ID",
        help="The ID(s) of the Puakma Application(s) to export",
        type=int,
    )
    export_parser.add_argument(
        "--out-dir",
        "-o",
        metavar="DIR",
        dest="export_dir",
        help="The destination folder. Default is 'exports' within the workspace.",
        type=Path,
    )
    export_parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=100,
        help="Set the timeout duration in seconds. Default is %(default)s.",
    )
    export_parser.add_argument(
        "--exclude-source",
        action="store_false",
        help="Exclude the .java source files",
        dest="include_source",
    )
    _add_server_option(export_parser)
    return export_parser


def add_watch_parser(command_parser: _SubParsersAction[ArgumentParser]) -> None:
    watch_parser = command_parser.add_parser(
        "watch",
        help=(
            "Watch the workspace for changes to Design Objects "
            "and upload them to the server"
        ),
    )
    _add_server_option(watch_parser)


def add_clean_parser(command_parser: _SubParsersAction[ArgumentParser]) -> None:
    clean_parser = command_parser.add_parser(
        "clean",
        help="Delete the cloned Puakma Application directories in the workspace",
    )
    clean_parser.add_argument(
        "--all",
        "-a",
        help="Set this flag to clean all servers",
        action="store_true",
    )
    _add_server_option(clean_parser)


def add_config_parser(command_parser: _SubParsersAction[ArgumentParser]) -> None:
    config_parser = command_parser.add_parser(
        "config", help="View and manage configuration"
    )
    config_mutex = config_parser.add_mutually_exclusive_group(required=True)
    config_mutex.add_argument(
        "--sample",
        dest="print_sample",
        action="store_true",
        help="Print a sample 'vortex-server-config.ini' file to the console",
    )
    config_mutex.add_argument(
        "--update-vscode-settings",
        action="store_true",
        help="Update the vortex.code-workspace file. Creating it if doesn't exist",
    )
    config_mutex.add_argument(
        "--reset-vscode-settings",
        action="store_true",
        help="Recreate the vortex.code-workspace file",
    )
    config_mutex.add_argument(
        "--output-config-path", action="store_true", help="Output the config file path"
    )
    config_mutex.add_argument(
        "--output-workspace-path", action="store_true", help="Output the workspace path"
    )
    config_mutex.add_argument(
        "--output-server-config",
        action="store_true",
        help="Output the current server definition in the config file.",
    )
    config_mutex.add_argument(
        "--list-servers",
        "-l",
        action="store_true",
        help="List the server definitions in the config file",
    )
    config_mutex.add_argument(
        "--set",
        help="Set an option value in a section. --set <section> <option> <value>",
        nargs=3,
        dest="set_config",
        metavar=("SECTION", "OPTION", "VALUE"),
    )
    _add_server_option(config_parser)


def add_log_parser(command_parser: _SubParsersAction[ArgumentParser]) -> None:
    log_parser = command_parser.add_parser(
        "log", help="View the last items in the server log"
    )
    log_parser.add_argument(
        "--limit",
        "-n",
        type=_check_int_in_range,
        help="The number of logs to return (max 50). Default is %(default)s",
        default=10,
    )
    log_parser.add_argument("--source", help="Filter the logs returned by their source")
    log_parser.add_argument(
        "--message", "-m", help="Filter the logs returned by their message"
    )
    log_type_mutex = log_parser.add_mutually_exclusive_group()
    log_type_mutex.add_argument("--errors-only", action="store_true")
    log_type_mutex.add_argument("--debug-only", action="store_true")
    log_type_mutex.add_argument("--info-only", action="store_true")
    log_parser.add_argument("--keep-alive", "-k", action="store_true")

    _positive_int = functools.partial(_check_int_in_range, min_=1)
    log_parser.add_argument(
        "--delay",
        "-d",
        type=_positive_int,
        help=(
            "Used only with --keep-alive. "
            "The number of seconds betwen requests for new logs. Default is %(default)s"
        ),
        default=5,
        metavar="SECONDS",
    )
    _add_server_option(log_parser)


def add_find_parser(command_parser: _SubParsersAction[ArgumentParser]) -> None:
    find_parser = command_parser.add_parser(
        "find",
        help="Search Design Objects of cloned applications",
        usage="%(prog)s [options] query",
    )
    find_parser.add_argument(
        "query", help="The query to search Design Objects. Default is search by name."
    )
    find_parser.add_argument("--app-id", type=int, nargs="*", dest="app_ids")
    find_parser.add_argument("--strict", "-z", action="store_true")
    query_mutex = find_parser.add_mutually_exclusive_group()
    query_mutex.add_argument(
        "--inherits-from", action="store_true", help="Search by inherits from instead"
    )
    query_mutex.add_argument(
        "--parent-page", action="store_true", help="Search by parent page instead"
    )
    find_parser.add_argument(
        "--ids-only",
        "-x",
        help="Display Object ID's in the output only",
        dest="show_ids_only",
        action="store_true",
    )
    find_parser.add_argument(
        "--show-params",
        help="Also display the Design Object parameters",
        action="store_true",
    )
    _add_design_type_option(find_parser)
    _add_server_option(find_parser)


def add_grep_parser(command_parser: _SubParsersAction[ArgumentParser]) -> None:
    grep_parser = command_parser.add_parser(
        "grep",
        help=(
            "Search the contents of cloned Design Objects using a Regular Expression."
        ),
        usage="%(prog)s [options] pattern",
    )
    grep_parser.add_argument("pattern", help="The Regular Expression pattern to match")
    grep_parser.add_argument("--app-id", type=int, nargs="*", dest="app_ids")

    grep_output_mutex = grep_parser.add_mutually_exclusive_group()
    grep_output_mutex.add_argument("--output-paths", action="store_true")
    grep_output_mutex.add_argument("--output-apps", action="store_true")

    grep_design_type_mutex = grep_parser.add_mutually_exclusive_group()
    grep_design_type_mutex.add_argument(
        "--include-resources",
        "-r",
        help="Set this flag to also search resources",
        action="store_true",
    )
    _add_design_type_option(grep_design_type_mutex)
    _add_server_option(grep_parser)


def add_new_parser(
    command_parser: _SubParsersAction[ArgumentParser],
) -> ArgumentParser:
    new_parser = command_parser.add_parser(
        "new",
        help="Create new Design Objects, Applications or Keywords",
    )

    _add_server_option(new_parser)

    sub_parser = new_parser.add_subparsers(dest="subcommand")

    # Object parser
    object_parser = sub_parser.add_parser(
        "object", aliases=("obj",), help="Create/Update Design Objects"
    )
    object_parser.add_argument(
        "--update",
        "-u",
        type=int,
        nargs="*",
        metavar="ID",
        dest="update_ids",
        help="Update mode. Entities with the given ID(s) are updated instead",
    )
    obj_optional_group = object_parser.add_argument_group("Design Object Options")
    _add_design_type_option(
        obj_optional_group,
        nargs=None,
        help_suffix=". Required when creating a new object.",
    )
    obj_optional_group.add_argument(
        "--app-id",
        type=int,
        help="Required when creating a new object.",
    )
    obj_optional_group.add_argument(
        "--name",
        "-n",
        help="Required when creating a new object.",
    )
    obj_optional_group.add_argument("--comment")
    obj_optional_group.add_argument("--inherit-from")
    obj_optional_group.add_argument("--open-action")
    obj_optional_group.add_argument("--save-action")
    obj_optional_group.add_argument("--parent-page")
    obj_optional_group.add_argument(
        "--content-type",
        help=(
            "The content/mime Type. "
            "Required when creating a 'resource' or 'documentation'"
        ),
    )

    # App Parser
    app_parser = sub_parser.add_parser("app", help="Create/Update Applications")
    app_parser.add_argument(
        "--name",
        "-n",
        help="The name of the application. Required if not updating.",
        type=_non_empty_string,
    )
    app_parser.add_argument(
        "--group",
        "-g",
        help="The application group",
        default="",
        type=lambda v: v.strip(),
    )

    optional_group = app_parser.add_argument_group(
        "Optional Arguments (Not applicable when importing)"
    )
    optional_group.add_argument(
        "--description", help="Brief description of the application"
    )
    optional_group.add_argument(
        "--inherit-from", help="Parent application to inherit from"
    )
    optional_group.add_argument(
        "--template", help="Template to base the application on"
    )

    # Keyword Parser
    keyword_parser = sub_parser.add_parser(
        "keyword", aliases=("kw",), help="Create/Update Keywords"
    )
    keyword_parser.add_argument("--app-id", type=int, required=True)
    keyword_parser.add_argument("--name", "-n", help="The keyword name", required=True)
    keyword_parser.add_argument("--values", nargs="*", required=True)

    return new_parser


def add_copy_parser(command_parser: _SubParsersAction[ArgumentParser]) -> None:
    copy_parser = command_parser.add_parser(
        "copy", help="Copy a Design Object from one application to another"
    )
    copy_parser.add_argument("ids", nargs="+", metavar="DESIGN_ID", type=int)
    copy_parser.add_argument(
        "--app-id",
        type=int,
        required=True,
        help="The App ID to copy the object to",
    )

    copy_parser.add_argument("--copy-params", action="store_true")
    _add_server_option(copy_parser)


def add_delete_parser(command_parser: _SubParsersAction[ArgumentParser]) -> None:
    delete_parser = command_parser.add_parser(
        "delete", help="Delete Design Object(s) by ID"
    )
    delete_parser.add_argument("obj_ids", nargs="+", type=int, metavar="DESIGN_ID")
    _add_server_option(delete_parser)


def add_db_parser(command_parser: _SubParsersAction[ArgumentParser]) -> ArgumentParser:
    db_parser = command_parser.add_parser("db", help="Interact with Databases")
    db_parser.add_argument(
        "database",
        help=(
            "The database name to connect to or the "
            "database connection ID if using --sql"
        ),
    )
    db_mutex = db_parser.add_mutually_exclusive_group(required=True)
    db_mutex.add_argument(
        "--sql",
        type=str,
        nargs="?",
        const="",
        help=(
            "The SQL query to execute. "
            "Requires <database> to be a database connection id (int). "
            "Interactively prompts for the sql if the value is empty (Non Windows)."
        ),
    )
    db_mutex.add_argument(
        "--schema",
        metavar="TABLE_NAME",
        help="View the schema of a table",
    )
    db_mutex.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List the tables in the Database",
    )
    sql_group = db_parser.add_argument_group("SQL Options")
    sql_group.add_argument(
        "--all-cols",
        "-a",
        action="store_false",
        help="Show all columns in the output. Default is max 6 columns",
        dest="truncate_cols",
    )
    sql_group.add_argument(
        "--limit",
        "-n",
        metavar="INT",
        type=_check_int_in_range,
        help=(
            "Default is %(default)s. "
            "The number of results to be returned between 1 and 50. "
            "This flag adds the 'LIMIT' clause of the given SQL query "
            "and so that clause should never be used when executing a query."
        ),
        default=10,
    )
    sql_group.add_argument(
        "--update",
        "-u",
        action="store_true",
        help="Set this flag when running querys for altering/updating the database",
    )
    return db_parser


def add_docs_parser(command_parser: _SubParsersAction[ArgumentParser]) -> None:
    command_parser.add_parser("docs", help="Open the Torndao Server Blackbook")


def add_execute_parser(command_parser: _SubParsersAction[ArgumentParser]) -> None:
    execute_parser = command_parser.add_parser(
        "execute",
        aliases=("ex",),
        help="Execute a command on the server. Execute '?' for more info.",
        description=_EXECUTE_PARSER_DESCRIPTION,
        formatter_class=RawDescriptionHelpFormatter,
    )
    execute_parser_mutex = execute_parser.add_mutually_exclusive_group(required=True)
    # 'cmd' here because 'command' conflicts with the command parser
    execute_parser_mutex.add_argument(
        "cmd",
        help="The command to execute",
        metavar="CMD",
        nargs="?",
        default="",
    )
    execute_parser_mutex.add_argument(
        "--refresh-design",
        type=int,
        help="Refresh an application's design",
        dest="refresh_app_id",
        metavar="APP_ID",
    )
    execute_parser_mutex.add_argument(
        "--run",
        type=Path,
        help=(
            "Run the action at the given local file path. "
            "Alias for 'tell agenda run /group/app.pma/action'"
        ),
        dest="run_action_path",
        metavar="DESIGN_PATH",
    )
    execute_parser_mutex.add_argument(
        "--schedule",
        action="store_true",
        help="View the agenda schedule. Alias for 'tell agenda schedule'",
    )
    _add_server_option(execute_parser)


def add_import_parser(
    command_parser: _SubParsersAction[ArgumentParser],
) -> ArgumentParser:
    import_parser = command_parser.add_parser(
        "import",
        help="Import a .pmx file to create an application.",
    )
    import_parser.add_argument(
        "pmx_path",
        metavar="PATH",
        help="Path to a .pmx file to create an application from.",
        type=_pmx_type,
    )
    import_parser.add_argument(
        "--name",
        "-n",
        help="The application name.",
        required=True,
        type=_non_empty_string,
    )
    import_parser.add_argument(
        "--group",
        "-g",
        help="The application group.",
        default="",
        type=lambda v: v.strip(),
    )
    _add_server_option(import_parser)
    return import_parser
