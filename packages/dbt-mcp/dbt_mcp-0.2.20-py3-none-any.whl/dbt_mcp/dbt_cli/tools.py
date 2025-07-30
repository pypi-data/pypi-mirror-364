import os
import subprocess
from collections.abc import Iterable, Sequence

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from dbt_mcp.config.config import DbtCliConfig
from dbt_mcp.prompts.prompts import get_prompt
from dbt_mcp.tools.definitions import ToolDefinition
from dbt_mcp.tools.register import register_tools
from dbt_mcp.tools.tool_names import ToolName


def create_dbt_cli_tool_definitions(config: DbtCliConfig) -> list[ToolDefinition]:
    def _run_dbt_command(
        command: list[str],
        selector: str | None = None,
        timeout: int | None = None,
        resource_type: list[str] | None = None,
        is_selectable: bool = False,
    ) -> str:
        try:
            # Commands that should always be quiet to reduce output verbosity
            verbose_commands = [
                "build",
                "compile",
                "docs",
                "parse",
                "run",
                "test",
                "list",
            ]

            if selector:
                selector_params = str(selector).split(" ")
                command = command + ["--select"] + selector_params

            if isinstance(resource_type, Iterable):
                command = command + ["--resource-type"] + resource_type

            full_command = command.copy()
            # Add --quiet flag to specific commands to reduce context window usage
            if len(full_command) > 0 and full_command[0] in verbose_commands:
                main_command = full_command[0]
                command_args = full_command[1:] if len(full_command) > 1 else []
                full_command = [main_command, "--quiet", *command_args]

            # We change the path only if this is an absolute path, otherwise we can have
            # problems with relative paths applied multiple times as DBT_PROJECT_DIR
            # is applied to dbt Core and Fusion as well (but not the dbt Cloud CLI)
            cwd_path = config.project_dir if os.path.isabs(config.project_dir) else None

            process = subprocess.Popen(
                args=[config.dbt_path, *full_command],
                cwd=cwd_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            output, _ = process.communicate(timeout=timeout)
            return output or "OK"
        except subprocess.TimeoutExpired:
            return "Timeout: dbt command took too long to complete." + (
                " Try using a specific selector to narrow down the results."
                if is_selectable
                else ""
            )
        except Exception as e:
            return str(e)

    def build(
        selector: str | None = Field(
            default=None, description=get_prompt("dbt_cli/args/selectors")
        ),
    ) -> str:
        return _run_dbt_command(["build"], selector, is_selectable=True)

    def compile() -> str:
        return _run_dbt_command(["compile"])

    def docs() -> str:
        return _run_dbt_command(["docs", "generate"])

    def ls(
        selector: str | None = Field(
            default=None, description=get_prompt("dbt_cli/args/selectors")
        ),
        resource_type: list[str] | None = Field(
            default=None,
            description=get_prompt("dbt_cli/args/resource_type"),
        ),
    ) -> str:
        return _run_dbt_command(
            ["list"],
            selector,
            timeout=config.dbt_cli_timeout,
            resource_type=resource_type,
            is_selectable=True,
        )

    def parse() -> str:
        return _run_dbt_command(["parse"])

    def run(
        selector: str | None = Field(
            default=None, description=get_prompt("dbt_cli/args/selectors")
        ),
    ) -> str:
        return _run_dbt_command(["run"], selector, is_selectable=True)

    def test(
        selector: str | None = Field(
            default=None, description=get_prompt("dbt_cli/args/selectors")
        ),
    ) -> str:
        return _run_dbt_command(["test"], selector, is_selectable=True)

    def show(
        sql_query: str = Field(description=get_prompt("dbt_cli/args/sql_query")),
        limit: int | None = Field(
            default=None, description=get_prompt("dbt_cli/args/limit")
        ),
    ) -> str:
        args = ["show", "--inline", sql_query, "--favor-state"]
        # This is quite crude, but it should be okay for now
        # until we have a dbt Fusion integration.
        cli_limit = None
        if "limit" in sql_query.lower():
            # When --limit=-1, dbt won't apply a separate limit.
            cli_limit = -1
        elif limit:
            # This can be problematic if the LLM provides
            # a SQL limit and a `limit` argument. However, preferencing the limit
            # in the SQL query leads to a better experience when the LLM
            # makes that mistake.
            cli_limit = limit
        if cli_limit is not None:
            args.extend(["--limit", str(cli_limit)])
        args.extend(["--output", "json"])
        return _run_dbt_command(args)

    return [
        ToolDefinition(
            fn=build,
            description=get_prompt("dbt_cli/build"),
        ),
        ToolDefinition(
            fn=compile,
            description=get_prompt("dbt_cli/compile"),
        ),
        ToolDefinition(
            fn=docs,
            description=get_prompt("dbt_cli/docs"),
        ),
        ToolDefinition(
            name="list",
            fn=ls,
            description=get_prompt("dbt_cli/list"),
        ),
        ToolDefinition(
            fn=parse,
            description=get_prompt("dbt_cli/parse"),
        ),
        ToolDefinition(
            fn=run,
            description=get_prompt("dbt_cli/run"),
        ),
        ToolDefinition(
            fn=test,
            description=get_prompt("dbt_cli/test"),
        ),
        ToolDefinition(
            fn=show,
            description=get_prompt("dbt_cli/show"),
        ),
    ]


def register_dbt_cli_tools(
    dbt_mcp: FastMCP,
    config: DbtCliConfig,
    exclude_tools: Sequence[ToolName] = [],
) -> None:
    register_tools(
        dbt_mcp,
        create_dbt_cli_tool_definitions(config),
        exclude_tools,
    )
