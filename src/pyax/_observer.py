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

from ApplicationServices import (
    AXObserverAddNotification,
    AXObserverCreateWithInfoCallback,
    AXObserverGetRunLoopSource,
    AXObserverRemoveNotification,
    AXObserverRef,
    AXUIElementCreateApplication,
)
from objc import callbackFor
from Quartz import (
    CFFileDescriptorCreate,
    CFFileDescriptorCreateRunLoopSource,
    CFFileDescriptorEnableCallBacks,
    CFRunLoopAddSource,
    CFRunLoopGetCurrent,
    CFRunLoopRun,
    CFRunLoopStop,
    kCFFileDescriptorReadCallBack,
    kCFRunLoopCommonModes,
    kCFRunLoopDefaultMode,
)
import os, fcntl, re

__all__ = ["start", "stop", "Observer"]

_SIGNAL_HANDLERS_ATTACHED = False

def stop():
    "Stop event loop"
    CFRunLoopStop(CFRunLoopGetCurrent())

def _handle_signals():
    global _SIGNAL_HANDLERS_ATTACHED
    if _SIGNAL_HANDLERS_ATTACHED:
        return

    r, w = os.pipe()

    cffd = CFFileDescriptorCreate(None, r, False, stop, None)
    CFFileDescriptorEnableCallBacks(cffd, kCFFileDescriptorReadCallBack)
    cfrlsrc = CFFileDescriptorCreateRunLoopSource(None, cffd, 0)
    CFRunLoopAddSource(CFRunLoopGetCurrent(), cfrlsrc, kCFRunLoopDefaultMode)

    def nop(signum, stackframe):
        pass

    import signal

    flags = fcntl.fcntl(w, fcntl.F_GETFL, 0)
    fcntl.fcntl(w, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    signal.set_wakeup_fd(w)
    signal.signal(signal.SIGINT, nop)
    signal.signal(signal.SIGTERM, nop)
    _SIGNAL_HANDLERS_ATTACHED = True


def start():
    "Start event loop"
    _handle_signals()
    CFRunLoopRun()

def create_observer(pid, callback, cfrunloop=None):
    """Create an observer for the given PID using the given callback for notifications.
    If a specific CFRunLoop needs to be attached to, it can be provided."""

    def _create_callback(callback):
        @callbackFor(AXObserverCreateWithInfoCallback)
        def cb(observer, element, notificationName, info, ptr):
            callback(observer, element, notificationName, info)

        return cb

    err, observer = AXObserverCreateWithInfoCallback(
        pid, _create_callback(callback), None
    )
    source = AXObserverGetRunLoopSource(observer)

    if cfrunloop:
        CFRunLoopAddSource(cfrunloop, source, kCFRunLoopCommonModes)
    else:
        CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)

    return observer


class AXObserverMixin(object):
    _mix_into = AXObserverRef

    # This hides all the useless attributes from AXObserver.
    def __dir__(self):
        return dir(AXObserverMixin)

    def add_notifications_for_element(self, element, *notification_names):
        "Registers the specified observer to receive notifications from the specified accessibility object."
        for name in notification_names:
            AXObserverAddNotification(self, element, name, None)

    def add_notifications(self, *notification_names):
        "Registers the specified observer to receive notifications from all accessibility objects in application"
        self.add_notifications_for_element(
            AXUIElementCreateApplication(self.pid), *notification_names
        )

    def remove_notifications_for_element(self, element, *notification_names):
        "Removes the specified notification from the list of notifications the observer wants to receive from the accessibility object."
        for name in notification_names:
            AXObserverRemoveNotification(self, element, name)

    def remove_notifications(self, *notification_names):
        "Removes the specified notification from the list of notifications the observer wants to receive from the application"
        self.remove_notifications_for_element(
            AXUIElementCreateApplication(self.pid), *notification_names
        )

    @property
    def pid(self):
        try:
            return int(re.search(r"pid=(\d+)", repr(self)).group(1))
        except:
            return 0
