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


from PyQt6 import QtGui, QtCore
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMainWindow


class Highlighter(QMainWindow):
    app = None

    def __init__(self, mouse_move_callback=None, click_callback=None):
        QMainWindow.__init__(self)

        transparent_for_input = (
            0
            if mouse_move_callback or click_callback
            else QtCore.Qt.WindowType.WindowTransparentForInput
        )

        self.setWindowFlags(
            QtCore.Qt.WindowType.WindowStaysOnTopHint
            | QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.BypassWindowManagerHint
            | QtCore.Qt.WindowType.NoDropShadowWindowHint
            | QtCore.Qt.WindowType.ExpandedClientAreaHint
            | transparent_for_input
        )
        self.setGeometry(QtGui.QGuiApplication.primaryScreen().availableGeometry())

        self.setStyleSheet("background-color: rgba(255, 0, 255, 0);")

        self.mouse_move_callback = mouse_move_callback
        self.click_callback = click_callback
        if self.mouse_move_callback:
            self.setMouseTracking(True)

        self.offset = 0
        self.label = QtWidgets.QLabel()
        self.label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        canvas = QtGui.QPixmap(QtGui.QGuiApplication.primaryScreen().availableSize())
        canvas.fill(QtCore.Qt.GlobalColor.transparent)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        self.showMaximized()

    def mouseMoveEvent(self, event):
        if self.mouse_move_callback:
            pos = event.globalPosition()
            self.mouse_move_callback(pos.x(), pos.y())

    def mousePressEvent(self, event):
        if self.click_callback:
            pos = event.globalPosition()
            self.click_callback(pos.x(), pos.y())

    def clear(self):
        canvas = self.label.pixmap()
        canvas.fill(QtCore.Qt.GlobalColor.transparent)
        self.label.setPixmap(canvas)

    def _normalize_alpha(self, colorstring):
        if colorstring.startswith("#") and len(colorstring) == 9:
            # QT expects an alpha color hex value in the format of #aarrggbb,
            # when the rest of the world expects #rrggbbaa
            return "#" + colorstring[-2:] + colorstring[1:-2]
        return colorstring

    def draw_rect(
        self, rect, fill="#00000000", stroke="#EB5160", stroke_width=1, flip_y=False
    ):
        if not rect:
            return
        canvas = self.label.pixmap()
        # canvas.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(canvas)
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor(self._normalize_alpha(fill)))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        if not stroke_width:
            stroke = "#00000000"
        pen = QtGui.QPen()
        pen.setWidth(stroke_width)
        pen.setColor(QtGui.QColor(self._normalize_alpha(stroke)))
        painter.setPen(pen)
        y = (
            rect["y"] - self.y()
            if not flip_y
            else QtGui.QGuiApplication.primaryScreen().size().height() - rect["y"]
        )
        painter.drawRect(rect["x"] - self.x(), y, rect["w"], rect["h"])
        painter.end()
        self.label.setPixmap(canvas)
