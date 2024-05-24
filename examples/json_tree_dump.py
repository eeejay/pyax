#!/usr/bin/env python3
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

import sys
import pyax
from pprint import pprint
import json

def element_to_dict(element, indent=0):
    attribute_names = filter(lambda x: x != "AXChildren", element.attribute_names)
    obj = dict([[attr_name, element[attr_name]] for attr_name in attribute_names])
    obj["actions"] = element.actions
    obj["AXChildren"] = [element_to_dict(child) for child in element]
    return obj

if __name__ == "__main__":
    app_name = sys.argv[-1]
    # acc = pyax.get_web_root(pyax.get_application_by_name(app_name))
    acc = pyax.get_application_by_name(app_name)
    obj = element_to_dict(acc)

    print(json.dumps(obj, indent=2, sort_keys=True, default=lambda x: str(x)))
