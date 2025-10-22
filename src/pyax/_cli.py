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

from rich.console import Console
from rich.json import JSON
from . import get_web_root, get_application_by_name, create_observer, start, EVENTS
from .utils import get_element_with_mouse
import sys

DEFAULT_ATTRIBUTES = ["AXRole", "AXTitle", "AXValue"]

_CONSOLE = Console()


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
            _print_error_and_exit("no web area found")
    if dom_id:
        element = element.search_for(lambda e: e["AXDOMIdentifier"] == dom_id)
        if not element:
            _print_error_and_exit(f"can't find '{dom_id}' DOM identifier in tree")

    return element


def _default_json_encoder(obj):
    try:
        return obj.serializable()
    except Exception:
        return repr(obj)


def _element_to_dict(
    element, attributes, all_attributes, list_attributes, list_actions
):
    attr_list = sorted(
        element.attribute_names if all_attributes else attributes,
        key=lambda x: [
            DEFAULT_ATTRIBUTES.index(x) if x in DEFAULT_ATTRIBUTES else len(attributes),
            x,
        ],
    )
    obj = dict([[attr_name, element[attr_name]] for attr_name in attr_list])
    if list_attributes:
        obj["attributes"] = sorted(
            element.attribute_names + element.parameterized_attribute_names
        )
    if list_actions:
        obj["actions"] = dict(
            [
                [action, element.get_action_description(action)]
                for action in element.actions
            ]
        )
    return obj


def _obj_to_pretty_string(element, obj, role_markup="bold red"):
    attr_string = " ".join(
        [
            f"[italic]{k[0]}[/italic]={repr(k[1])}"
            for k in filter(lambda x: x[0] != "AXRole", obj.items())
        ]
    )
    return f"[{role_markup}]{element['AXRole']}[/{role_markup}] {attr_string}"


def _json_dump_inner(
    element, attributes, all_attributes, list_attributes, list_actions
):
    obj = _element_to_dict(
        element, attributes, all_attributes, list_attributes, list_actions
    )
    obj["AXChildren"] = [
        _json_dump_inner(
            child, attributes, all_attributes, list_attributes, list_actions
        )
        for child in element
    ]
    return obj


def _json_dump(
    element,
    attributes,
    all_attributes,
    list_attributes,
    list_actions,
    show_subtree=True,
):
    attrs = element.attribute_names if all_attributes else attributes[:]
    data = (
        _element_to_dict(element, attrs, all_attributes, list_attributes, list_actions)
        if not show_subtree
        else _json_dump_inner(
            element, attrs, all_attributes, list_attributes, list_actions
        )
    )
    _CONSOLE.print(JSON.from_data(data, default=_default_json_encoder))


def _tree_dump(
    element,
    attributes,
    all_attributes,
    list_attributes,
    list_actions,
    indent=0,
    show_subtree=True,
):
    obj = _element_to_dict(
        element, attributes, all_attributes, list_attributes, list_actions
    )
    if "AXChildren" in obj and show_subtree:
        obj.pop("AXChildren")
    to_print = _obj_to_pretty_string(element, obj)
    _CONSOLE.print(f"{indent * ' '}{to_print}")
    if not show_subtree:
        return

    for child in element:
        _tree_dump(
            child, attributes, all_attributes, list_attributes, list_actions, indent + 1
        )


def _create_notification_dumper(
    attributes, print_info, all_attributes, list_attributes, list_actions
):
    def dump_notification(_, element, notificationName, info):
        obj = _element_to_dict(
            element, attributes, all_attributes, list_attributes, list_actions
        )
        if "AXChildren" in obj:
            obj.pop("AXChildren")
        to_print = _obj_to_pretty_string(element, obj, "red")
        _CONSOLE.print(f"[bold]{notificationName.ljust(25)}[/bold] {to_print}")
        if print_info:
            if info:
                _CONSOLE.print(JSON.from_data(info, default=_default_json_encoder))
            _CONSOLE.print()

    return dump_notification


def tree(
    app_name,
    web,
    dom_id,
    attributes,
    all_attributes,
    list_attributes,
    list_actions,
    json,
):
    element = _get_target_uielement(_get_target_application(app_name), web, dom_id)

    if json:
        _json_dump(element, attributes, all_attributes, list_attributes, list_actions)
    else:
        _tree_dump(element, attributes, all_attributes, list_attributes, list_actions)


def observe(
    app_name,
    events,
    attributes,
    all_attributes,
    list_attributes,
    list_actions,
    print_info,
):
    app = get_application_by_name(app_name)
    observer = create_observer(
        app.pid,
        _create_notification_dumper(
            attributes, print_info, all_attributes, list_attributes, list_actions
        ),
    )
    observer.add_notifications(*(events or EVENTS))
    start()


def inspect(
    app_name,
    dom_id,
    attributes,
    all_attributes,
    list_attributes,
    list_actions,
    show_subtree,
    json,
):
    app = _get_target_application(app_name)

    def _onhover(element):
        elem_str = repr(element)[: _CONSOLE.width].ljust(_CONSOLE.width)
        _CONSOLE.print(elem_str, end="\r")

    def _show(element):
        if json:
            _json_dump(
                element,
                attributes,
                all_attributes,
                list_attributes,
                list_actions,
                show_subtree=show_subtree,
            )
        else:
            _tree_dump(
                element,
                attributes,
                all_attributes,
                list_attributes,
                list_actions,
                show_subtree=show_subtree,
            )

    if dom_id:
        _show(_get_target_uielement(app_name, None, dom_id))
        return

    try:
        element = get_element_with_mouse(app, _onhover)
    except NotImplementedError:
        _print_error_and_exit(
            "'highlight' pyax extra is required for inspecting element under mouse"
        )

    print()
    _show(element)
