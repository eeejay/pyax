# pyax

Client library for macOS accessibility

The library provides convenient entry points for retreiving accessible objects, and setting up notification observers.

This library also Pythonifies `AXUIElement` and `AXObserver` and provides easy ways to access attributes, query the accessible element's heirarchy.

## Installation

```bash
$ pip install pyax
```

## Usage

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
