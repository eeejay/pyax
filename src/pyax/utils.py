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

from . import get_application_by_name, get_element_at_position, start, stop

try:
    from ._highlighter import Highlighter
except ModuleNotFoundError:
    Highlighter = None


def get_element_with_mouse(app, hover_callback=None):
    if not Highlighter:
        raise NotImplementedError(
            "'highlight' pyax extra is required for `get_element_with_mouse`"
        )
    app_element = get_application_by_name(app) if type(app) is str else app
    element = None

    def _mm(x, y):
        nonlocal element
        if element:
            return
        elem = get_element_at_position(app_element, x, y)
        if not elem:
            return
        highlighter.clear()
        highlighter.draw_rect(
            elem["AXFrame"], fill="#1982C455", stroke="#1982C4", stroke_width=1
        )
        if hover_callback:
            hover_callback(elem)

    def _click(x, y):
        nonlocal element
        if element:
            element = None
            _mm(x, y)
            return
        element = get_element_at_position(app_element, x, y)
        stop()

    highlighter = Highlighter(_mm, _click)

    start()

    return element
