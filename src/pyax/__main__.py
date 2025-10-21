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

import sys
import typer
from typing_extensions import Annotated
from . import get_web_root, get_application_by_name, create_observer, start, EVENTS
from ._cli import json_dump, tree_dump, create_notification_dumper, DEFAULT_ATTRIBUTES
from typing import List
from rich import print
from rich.json import JSON

app = typer.Typer()

def _print_error_and_exit(s):
    print(f"Error: {s}", file=sys.stderr)
    sys.exit(1)


def _get_target_application(app_name):
    app = get_application_by_name(app_name)
    if not app:
        _print_error_and_exit(f"application '{app_name}' not found")
    return app

def _get_target_uielement(app, web, dom_id):
    element = app
    if web or dom_id:
        element = get_web_root(element)
        if not element:
            _print_error_and_exit(f"application '{app_name}' does not have a web area")
    if dom_id:
        element = element.search_for(lambda e: e["AXDOMIdentifier"] == dom_id)
        if not element:
            _print_error_and_exit(f"can't find '{dom_id}' DOM identifier in tree")

    return element

@app.command()
def tree(app_name: Annotated[str, typer.Argument(help="Application to examine")],
         web: Annotated[bool, typer.Option("--web", "-w", help="Only output web area subtree")] = False,
         dom_id: Annotated[str, typer.Option(help="Only output subtree of DOM node ID")] = None,
         attributes: Annotated[List[str], typer.Option("--attribute", "-a", help="Show provided attributes")] = DEFAULT_ATTRIBUTES,
         all_attributes: Annotated[bool, typer.Option(help="Show all available attribute values on each node")] = False,
         list_attributes: Annotated[bool, typer.Option(help="List available attributes on each node")] = False,
         list_actions: Annotated[bool, typer.Option(help="List available actions and their description on each node")] = False,
         json: Annotated[bool, typer.Option(help="Output in JSON format")] = False):
    element = _get_target_uielement(_get_target_application(app_name), web, dom_id)

    if json:
        json_dump(element, attributes, all_attributes, list_attributes, list_actions)
    else:
        tree_dump(element, attributes, all_attributes, list_attributes, list_actions)

@app.command()
def observe(app_name: Annotated[str, typer.Argument(help="Application to examine")],
            events: Annotated[List[str], typer.Option("--event", "-e", help="Show provided events")] = None,
            attributes: Annotated[List[str], typer.Option("--attribute", "-a", help="Show provided attributes")] = DEFAULT_ATTRIBUTES,
            all_attributes: Annotated[bool, typer.Option(help="Show all available attribute values on each node")] = False,
            list_attributes: Annotated[bool, typer.Option(help="List available attributes on each node")] = False,
            list_actions: Annotated[bool, typer.Option(help="List available actions and their description on each node")] = False,
            print_info: Annotated[bool, typer.Option(help="Print bundled notification info")] = False):
    app = get_application_by_name(app_name)
    observer = create_observer(app.pid, create_notification_dumper(attributes, print_info, all_attributes, list_attributes, list_actions))
    observer.add_notifications(*(events or EVENTS))
    start()


if __name__ == "__main__":
    app()
