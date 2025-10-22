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

import types
import re
from ApplicationServices import (
    AXCustomContent,
    AXValueRef,
    AXTextMarkerRef,
    AXTextMarkerRangeRef,
    AXValueGetType,
    kAXValueCFRangeType,
    kAXValueCGPointType,
    kAXValueCGRectType,
    kAXValueCGSizeType,
)

from Cocoa import NSDictionary, NSURL, NSArray
from pyax._uielement import AXUIElementMixin
from pyax._observer import AXObserverMixin

__all__ = ["mix_classes"]


def _mix_class(new_cls, ignore=[]):
    """
    Adds the methods in new_cls to cls. After mixing, all instances of cls will
    have the new methods. If there is a method name clash, the method already
    in cls will be prefixed with '_mix_' before the new method of the same
    name is mixed in.

    @note: _ is not the prefix because if you wind up with __ in front of a
    variable, it becomes private and mangled when an instance is created.
    Difficult to invoke from the mixin class.

    @param new_cls: Class containing features to add
    @type new_cls: class
    @param ignore: Ignore these methods from the mixin
    @type ignore: iterable
    """
    cls = new_cls._mix_into
    if not cls:
        raise TypeError("mix class needs a _mix_into defined")
    delattr(new_cls, "_mix_into")

    # loop over all names in the new class
    setattr(cls, "_mixed", {})
    for name, func in list(new_cls.__dict__.items()):
        if name in ignore:
            continue
        if isinstance(func, types.FunctionType):
            # build a new function that is a clone of the one from new_cls
            method = types.FunctionType(
                func.__code__,
                func.__globals__,
                name,
                func.__defaults__,
                func.__closure__,
            )
            try:
                # check if a method of the same name already exists in the
                # target
                old_method = getattr(cls, name)
            except AttributeError:
                pass
            else:
                # rename the old method so we can still call it if need be
                cls._mixed[name] = old_method
            # add the clone to cls
            setattr(cls, name, method)
        elif isinstance(func, staticmethod):
            try:
                # check if a method of the same name already exists
                # in the target
                old_method = getattr(cls, name)
            except AttributeError:
                pass
            else:
                # rename the old method so we can still call it if need be
                cls._mixed[name] = old_method
            setattr(cls, name, func)
        elif isinstance(func, property):
            try:
                # check if a method of the same name already exists
                # in the target
                getattr(cls, name)
            except AttributeError:
                pass
            else:
                # IMPORTANT: We save the old property before overwriting it,
                # even though we never end up calling the old prop from our
                # mixin class If we don't save the old one, we seem to
                # introduce a Python ref count problem where the property
                # get/set methods disappear before we can use them at a later
                # time. This is a minor waste of memory because a property is
                # a class object and we only overwrite a few of them.
                cls._mixed[name] = old_method
            setattr(cls, name, func)


class NSDictionaryMixin(object):
    _mix_into = NSDictionary

    def __repr__(self):
        keys = list(self)
        return repr(dict(zip(keys, [self[k] for k in keys])))

    def serializable(self):
        keys = list(self)
        return dict(zip(keys, [self[k] for k in keys]))


class NSURLMixin(object):
    _mix_into = NSURL

    def __repr__(self):
        return repr(self.description())


class AXTextMarkerMixin(object):
    _mix_into = AXTextMarkerRef

    def __repr__(self):
        address = re.findall(
            r"<AXTextMarker (0x[0-9a-f]+) \[0x[0-9a-f]+\]", self.description()
        )[0]
        return f"AXTextMarker({address})"

    def serializable(self):
        return "<AXTextMarker>"


class AXTextMarkerRangeMixin(object):
    _mix_into = AXTextMarkerRangeRef

    def __repr__(self):
        address = re.findall(
            r"<AXTextMarkerRange (0x[0-9a-f]+) \[0x[0-9a-f]+\]", self.description()
        )[0]
        return f"AXTextMarkerRange({address})"

    def serializable(self):
        return "<AXTextMarkerRange>"


class NSArrayMixin(object):
    _mix_into = NSArray

    def __repr__(self):
        return repr(list(self))

    def serializable(self):
        return list(self)


class AXCustomContentMixin(object):
    _mix_into = AXCustomContent

    def __repr__(self):
        return "AXCustomContent(%s)" % (str({self.label(): self.value()}))

    def serializable(self):
        return {self.label(): self.value()}


class AXValueRefMixin(object):
    _mix_into = AXValueRef

    _ax_type_map = {
        kAXValueCGSizeType: (float, "Size"),
        kAXValueCGPointType: (float, "Point"),
        kAXValueCFRangeType: (int, "Range"),
        kAXValueCGRectType: (float, "Rect"),
    }

    def value_type(self):
        ax_attr_type = AXValueGetType(self)
        try:
            return AXValueRefMixin._ax_type_map[ax_attr_type][1]
        except KeyError:
            raise Exception(
                "Value type not supported yet: {}".format(self.description())
            )

    def to_dict(self):
        ax_attr_type = AXValueGetType(self)
        try:
            matches = re.findall(r"(?:((\w+):(\S+)))+", self.description())
            return dict(
                [
                    [m[1], AXValueRefMixin._ax_type_map[ax_attr_type][0](m[2])]
                    for m in matches
                ]
            )
        except KeyError:
            raise Exception(
                "Value type not supported yet: {}".format(self.description())
            )

    def serializable(self):
        return self.to_dict()

    def __repr__(self):
        return f"AXValue({self.value_type()}({repr(self.to_dict())}))"

    def __getitem__(self, key):
        return self.to_dict()[key]


def mix_classes():
    _mix_class(AXUIElementMixin)
    _mix_class(AXCustomContentMixin)
    _mix_class(AXObserverMixin)
    _mix_class(NSDictionaryMixin)
    _mix_class(NSURLMixin)
    _mix_class(NSArrayMixin)
    _mix_class(AXValueRefMixin)
    _mix_class(AXTextMarkerMixin)
    _mix_class(AXTextMarkerRangeMixin)
