# pyax

Client library for macOS accessibility

The library provides convenient entry points for retreiving accessible objects, and setting up notification observers.

This library also Pythonifies `AXUIElement` and `AXObserver` and provides easy ways to access attributes, query the accessible element's heirarchy.

## Installation

```bash
$ pip install pyax[highlight]
```

## Usage

### Command Line

#### Inspecting an element

The `inspect` command allows you to select an element under the pointer for inspection, and print out any interesting information about the object. This command requires the `highlight` extra.

![inspect demo screencast](inspect_demo.gif)

#### Examining the accessible tree

The `tree` command allows you to dump the current tree of an application, web app or specific subtree. You can choose which attributes to show, or show all available attributes. You can list actions, and you can output the tree in a JSON format.

```sh
% pyax tree Safari -w -a AXTitle -a AXValue -a AXSubrole
AXWebArea AXTitle='' AXValue='' AXSubrole=None
 AXGroup AXTitle='' AXValue='' AXSubrole=None
  AXStaticText AXTitle='' AXValue='Name:' AXSubrole=None
   AXStaticText AXTitle='' AXValue='Name:' AXSubrole=None
  AXTextField AXTitle='Name:' AXValue='John' AXSubrole=None
   AXGroup AXTitle='' AXValue='' AXSubrole='AXEmptyGroup'
 AXGroup AXTitle='' AXValue='' AXSubrole=None
  AXStaticText AXTitle='' AXValue='Email:' AXSubrole=None
   AXStaticText AXTitle='' AXValue='Email:' AXSubrole=None
  AXTextField AXTitle='Email:' AXValue='john@example.com' AXSubrole=None
   AXGroup AXTitle='' AXValue='' AXSubrole='AXEmptyGroup'
 AXGroup AXTitle='' AXValue='' AXSubrole=None
  AXStaticText AXTitle='' AXValue='Message:' AXSubrole=None
   AXStaticText AXTitle='' AXValue='Message:' AXSubrole=None
  AXTextArea AXTitle='Message:' AXValue='hi its me' AXSubrole=None
   AXGroup AXTitle='' AXValue='' AXSubrole=None
    AXStaticText AXTitle='' AXValue='hi its me' AXSubrole=None
```

#### Observing accessible notifications

The `Observe` command allows you to observe any give accessibility notification an app may emit, and the associated data with that notification.

```sh
% pyax observe Safari
AXFocusedUIElementChanged AXTextArea AXTitle='Message:' AXValue='hi its me'
AXSelectedTextChanged     AXTextArea AXTitle='Message:' AXValue='hi its me. '
```

### API

See `examples` directory for in-depth use.

Here is what a basic interactive session could look like:

```pycon
>>> import pyax
>>> app = pyax.get_application_by_name('Safari')
>>> print(app)
[AXApplication | Safari]
>>> web_root = app.search_for(lambda e: e["AXRole"] == "AXWebArea")
>>> print(web_root)
[AXWebArea | ]
>>> for child in web_root:
...     print(child, child["AXDOMIdentifier"])
[AXGroup | ] content
[AXHeading | Navigation menu]
[AXGroup | ] p-personal
[AXGroup | ] p-namespaces
[AXGroup | ] p-views
[AXGroup | ] p-search
[AXGroup | ] p-logo
[AXGroup | ] p-navigation
[AXGroup | ] p-interaction
[AXGroup | ] p-tb
[AXGroup | ] p-coll-print_export
[AXGroup | ] p-wikibase-otherprojects
[AXGroup | ] p-lang
[AXGroup | ] footer
```

## License

`pyax` was created by Eitan Isaacson. It is licensed under the terms of the MIT license.
