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

# This script demostrates how to grab an a11y tree from the simulator.

import pyax

TRAITS = [
    # "AXTraitNone",
    "AXTraitButton",
    "AXTraitLink",
    "AXTraitImage",
    "AXTraitSelected",
    "AXTraitPlaysSound",
    "AXTraitKeyboardKey",
    "AXTraitStaticText",
    "AXTraitSummaryElement",
    "AXTraitNotEnabled",
    "AXTraitUpdatesFrequently",
    "AXTraitSearchField",
    "AXTraitStartsMediaSession",
    "AXTraitAdjustable",
    "AXTraitAllowsDirectInteraction",
    "AXTraitCausesPageTurn",
    "AXTraitTabBar",
    "AXTraitHeader",
    "AXTraitWebContent",
    "AXTraitTextEntry",
    "AXTraitPickerElement",
    "AXTraitRadioButton",
    "AXTraitIsEditing",
    "AXTraitLaunchIcon",
    "AXTraitStatusBarElement",
    "AXTraitSecureTextField",
    "AXTraitInactive",
    "AXTraitFooter",
    "AXTraitBackButton",
    "AXTraitTabButton",
    "AXTraitAutoCorrectCandidate",
    "AXTraitDeleteKey",
    "AXTraitSelectionDismissesItem",
    "AXTraitVisited",
    "AXTraitScrollable",
    "AXTraitSpacer",
    "AXTraitTableIndex",
    "AXTraitMap",
    "AXTraitTextOperationsAvailable",
    "AXTraitDraggable",
    "AXTraitGesturePracticeRegion",
    "AXTraitPopupButton",
    "AXTraitAllowsNativeSliding",
    "AXTraitMathEquation",
    "AXTraitContainedByTable",
    "AXTraitContainedByList",
    "AXTraitTouchContainer",
    "AXTraitSupportsZoom",
    "AXTraitTextArea",
    "AXTraitBookContent",
    "AXTraitContainedByLandmark",
    "AXTraitFolderIcon",
    "AXTraitReadOnly",
    "AXTraitMenuItem",
    "AXTraitToggle",
    "AXTraitIgnoreItemChooser",
    "AXTraitSupportsTrackingDetail",
    "AXTraitAlert",
    "AXTraitContainedByFieldset",
    "AXTraitAllowsLayoutChangeInStatusBar",
]

def traits_to_string(traits):
    if not traits:
        return "AXTraitNone"
    trait_strings = []
    for i in range(len(TRAITS)):
        if (1 << i) & traits:
            trait_strings.append(TRAITS[i])
    return ','.join(trait_strings)

def attr_to_str(elem, attr):
    value = elem[attr]
    if not value:
        return None
    if attr == "AXTraits":
        return "%s=[%s]" % (attr, traits_to_string(value))
    return "%s=%s" % (attr, repr(value))

def tree_dump(element, indent=0):
    attribs = ["AXDescription", "AXValue", "AXTraits"]
    entries = filter(lambda x: x is not None, [attr_to_str(element, attr) for attr in attribs])
    print("%s %s %s" % (indent * " ", element, ', '.join(entries)))
    for child in element:
        tree_dump(child, indent + 1)

if __name__ == "__main__":
    app_name = "Simulator"
    acc = pyax.get_application_by_name(app_name)
    acc = acc.search_for(lambda a: a["AXSubrole"] == "iOSContentGroup")
    tree_dump(acc)
