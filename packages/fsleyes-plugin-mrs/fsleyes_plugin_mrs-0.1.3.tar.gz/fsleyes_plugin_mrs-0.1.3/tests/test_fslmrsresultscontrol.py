#!/usr/bin/env python

'''
test_fslmrsresultscontrol.py - Tests methods of FSLMRSResultsControl class in tools.py

Authors: Vasilis Karlaftis    <vasilis.karlaftis@ndcn.ox.ac.uk>

Elements taken from fsleyes/fsleyes/tests/controls/test_controls.py by Paul McCarthy <pauldmccarthy@gmail.com>

Copyright (C) 2025 University of Oxford
'''

import os.path as op
from pathlib import Path
import fsl.data.image as fslimage
from tests import run_with_viewpanel, realYield

from fsleyes_plugin_mrs.tools       import FSLMRSResultsControl
from fsleyes.views.orthopanel       import OrthoPanel

datadir = Path(__file__).parent / 'testdata' / 'svs'

# Test #1: check if the title matches the expected value
def test_FSLMRSResultsControl_title():
    assert isinstance(FSLMRSResultsControl.title(), str)
    assert FSLMRSResultsControl.title() == "FSL-MRS Results"

# Test #2: check if supportedViews include the MRSView
def test_FSLMRSResultsControl_supportedViews():
    assert isinstance(FSLMRSResultsControl.supportedViews(), list)
    assert OrthoPanel in FSLMRSResultsControl.supportedViews()

# Test #3: check FSLMRSResultsControl basic functionality on a single metabolite file
def test_FSLMRSResultsControlPanel():
    run_with_viewpanel(_test_FSLMRSResultsControlPanel, OrthoPanel)

def _test_FSLMRSResultsControlPanel(view, overlayList, displayCtx):

    img = fslimage.Image(op.join(datadir, 'metab'))
    overlayList.append(img)
    realYield(25)

    # toggle the panel off and on
    view.togglePanel(FSLMRSResultsControl)
    realYield(25)

    view.togglePanel(FSLMRSResultsControl)
    realYield(25)
