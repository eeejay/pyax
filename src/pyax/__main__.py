# The MIT License(MIT)
#
# Copyright(c) 2025 Eitan Isaacson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import typer
from typing_extensions import Annotated
from typing import List
from ._cli import tree as cli_tree
from ._cli import observe as cli_observe
from ._cli import inspect as cli_inspect
from ._cli import DEFAULT_ATTRIBUTES

app = typer.Typer(add_completion=False)


@app.command()
def tree(
    app_name: Annotated[str, typer.Argument(help="Application to examine")],
    web: Annotated[
        bool, typer.Option("--web", "-w", help="Only output web area subtree")
    ] = False,
    dom_id: Annotated[
        str, typer.Option(help="Only output subtree of DOM node ID")
    ] = None,
    attributes: Annotated[
        List[str], typer.Option("--attribute", "-a", help="Show provided attributes")
    ] = DEFAULT_ATTRIBUTES,
    all_attributes: Annotated[
        bool, typer.Option(help="Show all available attribute values on each node")
    ] = False,
    list_attributes: Annotated[
        bool, typer.Option(help="List available attributes on each node")
    ] = False,
    list_actions: Annotated[
        bool,
        typer.Option(help="List available actions and their description on each node"),
    ] = False,
    json: Annotated[bool, typer.Option(help="Output in JSON format")] = False,
):
    cli_tree(
        app_name,
        web,
        dom_id,
        attributes,
        all_attributes,
        list_attributes,
        list_actions,
        json,
    )


@app.command()
def observe(
    app_name: Annotated[str, typer.Argument(help="Application to examine")],
    events: Annotated[
        List[str], typer.Option("--event", "-e", help="Show provided events")
    ] = None,
    attributes: Annotated[
        List[str], typer.Option("--attribute", "-a", help="Show provided attributes")
    ] = DEFAULT_ATTRIBUTES,
    all_attributes: Annotated[
        bool, typer.Option(help="Show all available attribute values on each node")
    ] = False,
    list_attributes: Annotated[
        bool, typer.Option(help="List available attributes on each node")
    ] = False,
    list_actions: Annotated[
        bool,
        typer.Option(help="List available actions and their description on each node"),
    ] = False,
    print_info: Annotated[
        bool, typer.Option(help="Print bundled notification info")
    ] = False,
):
    cli_observe(
        app_name,
        events,
        attributes,
        all_attributes,
        list_attributes,
        list_actions,
        print_info,
    )


@app.command()
def inspect(
    app_name: Annotated[str, typer.Argument(help="Application to examine")],
    dom_id: Annotated[
        str, typer.Option(help="Only output subtree of DOM node ID")
    ] = None,
    attributes: Annotated[
        List[str], typer.Option("--attribute", "-a", help="Show provided attributes")
    ] = DEFAULT_ATTRIBUTES,
    all_attributes: Annotated[
        bool, typer.Option(help="Show all available attribute values on each node")
    ] = False,
    list_attributes: Annotated[
        bool, typer.Option(help="List available attributes on each node")
    ] = False,
    list_actions: Annotated[
        bool,
        typer.Option(help="List available actions and their description on each node"),
    ] = False,
    show_subtree: Annotated[
        bool, typer.Option(help="Print the subtree of the inspected element")
    ] = False,
    json: Annotated[bool, typer.Option(help="Output in JSON format")] = False,
):
    cli_inspect(
        app_name,
        dom_id,
        attributes,
        all_attributes,
        list_attributes,
        list_actions,
        show_subtree,
        json,
    )


def version_callback(value: bool):
    from . import __version__

    print(__version__)
    raise typer.Exit()


@app.callback()
def version(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Print the version and exit",
    )
):
    pass


if __name__ == "__main__":
    app()
