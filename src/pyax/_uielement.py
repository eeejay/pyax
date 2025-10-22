# The MIT License(MIT)
#
# Copyright(c) 2022 Eitan Isaacson
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

import re
from ApplicationServices import (
    AXUIElementRef,
    AXUIElementCopyAttributeNames,
    AXUIElementCopyAttributeValue,
    AXUIElementCopyParameterizedAttributeValue,
    AXUIElementCopyParameterizedAttributeNames,
    AXUIElementIsAttributeSettable,
    AXUIElementCopyActionNames,
    AXUIElementSetAttributeValue,
    AXUIElementCreateApplication,
    AXUIElementCopyMultipleAttributeValues,
    AXUIElementCopyActionDescription,
    AXUIElementPerformAction,
    AXUIElementCopyElementAtPosition,
    AXValueRef,
    AXValueGetType,
    kAXValueAXErrorType,
)
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListExcludeDesktopElements,
    kCGNullWindowID,
)
from Foundation import NSKeyedUnarchiver
from Cocoa import NSData

__all__ = [
    "AXUIElementMixin",
    "get_applications",
    "get_application_by_name",
    "get_web_root",
    "get_element_at_position",
]


def _unarchiveObject(val):
    if isinstance(val, NSData):
        try:
            return NSKeyedUnarchiver.unarchiveObjectWithData_(val)
        except Exception:
            return val
    else:
        return val


def get_applications():
    wl = CGWindowListCopyWindowInfo(
        kCGWindowListExcludeDesktopElements, kCGNullWindowID
    )
    pids = [int((w.valueForKey_("kCGWindowOwnerPID"))) for w in wl]
    return [AXUIElementCreateApplication(pid) for pid in set(pids)]


def get_application_by_name(name):
    wl = CGWindowListCopyWindowInfo(
        kCGWindowListExcludeDesktopElements, kCGNullWindowID
    )
    for w in wl:
        if name == w.valueForKey_("kCGWindowOwnerName"):
            return AXUIElementCreateApplication(
                int((w.valueForKey_("kCGWindowOwnerPID")))
            )


def get_application_from_pid(pid):
    return AXUIElementCreateApplication(pid)


def get_web_root(acc):
    return acc.search_for(lambda e: e["AXRole"] == "AXWebArea")


def get_element_at_position(app, x, y):
    err, element = AXUIElementCopyElementAtPosition(app, x, y, None)
    return element


class AXUIElementMixin(object):
    _mix_into = AXUIElementRef

    # This hides all the useless attributes from AXUIElement.
    def __dir__(self):
        return dir(AXUIElementMixin)

    @property
    def attribute_names(self):
        "Returns a list of all the attributes supported by the specified accessibility object."
        err, attr = AXUIElementCopyAttributeNames(self, None)
        return sorted(list(attr))

    @property
    def parameterized_attribute_names(self):
        "Returns a list of all the parameterized attributes supported by the specified accessibility object."
        err, attr = AXUIElementCopyParameterizedAttributeNames(self, None)
        return sorted(list(attr))

    def is_attribute_settable(self, attribute):
        "Returns whether the specified accessibility object's attribute can be modified."
        err, result = AXUIElementIsAttributeSettable(self, attribute, None)
        return bool(result)

    def get_attribute_value(self, attribute):
        "Returns the value of an accessibility object's attribute."
        err, value = AXUIElementCopyAttributeValue(self, attribute, None)
        return _unarchiveObject(value)

    def get_attribute_parameterized_value(self, attribute, parameter):
        "Returns the value of an accessibility object's parameterized attribute."
        err, value = AXUIElementCopyParameterizedAttributeValue(
            self, attribute, parameter, None
        )
        return _unarchiveObject(value)

    def __getitem__(self, key):
        """Returns the value of an accessibility object's attribute.
        If a two member tuple is provided with an attribute name and parameter,
        returns the value of an accessibility object's parameterized attribute."""
        if type(key) is tuple and len(key) == 2:
            return self.get_attribute_parameterized_value(*key)
        return self.get_attribute_value(key)

    def __setitem__(self, key, value):
        "Sets the accessibility object's attribute to the specified value."
        AXUIElementSetAttributeValue(self, key, value)

    def get_multiple_attribute_values(self, *attributes):
        "Returns the values of multiple attributes in the accessibility object."
        err, values = AXUIElementCopyMultipleAttributeValues(self, attributes, 0, None)
        rv = {}
        for i, value in enumerate(values or []):
            if isinstance(value, AXValueRef):
                if AXValueGetType(value) == kAXValueAXErrorType:
                    continue
            rv[attributes[i]] = _unarchiveObject(value)
        return rv

    @property
    def actions(self):
        "Returns a list of all the actions the specified accessibility object can perform."
        err, result = AXUIElementCopyActionNames(self, None)
        return sorted(list(result) if result else [])

    def get_action_description(self, action_name):
        "Returns a localized description of the specified accessibility object's action."
        err, result = AXUIElementCopyActionDescription(self, action_name, None)
        return result

    def perform_action(self, action_name):
        "Performs the specified action on the accessibility object."
        result = AXUIElementPerformAction(self, action_name)
        return result

    def __len__(self):
        "Returns the children count."
        return len(self["AXChildren"] or [])

    def __iter__(self):
        "Iterate over children."
        children = self["AXChildren"]
        for child in children or []:
            yield child

    @property
    def parent(self):
        return self["AXParent"]

    def __repr__(self):
        attrs = {}
        for attr in ["AXTitle", "AXDescription", "AXValue"]:
            val = self[attr]
            if val:
                attrs[attr] = val
        return "AXUIElement(%s: %s)" % (
            self["AXRole"],
            " ".join([f"{k}={repr(attrs[k])}" for k in attrs]),
        )

    def __bool__(self):
        return True

    def search_for(self, match_func):
        "Recursively search in element's subtree for descendant that matches prerequisite"
        if match_func(self):
            return self
        for child in self:
            match = child.search_for(match_func)
            if match:
                return match

        return None

    @property
    def pid(self):
        try:
            return int(re.search(r"pid=(\d+)", self._mixed["__repr__"](self)).group(1))
        except Exception:
            return 0
