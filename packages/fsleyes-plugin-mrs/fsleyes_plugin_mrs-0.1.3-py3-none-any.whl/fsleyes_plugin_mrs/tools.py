#!/usr/bin/env python
#
# tools.py - Contains the Tool-related classes for loading fsl_mrsi results
# 1) FSLFitTool class - The Tool class
# 2) FSLMRSResultsControl class - The new Control panel in OrthoView
#
# Author: Will Clarke <william.clarke@ndcn.ox.ac.uk>
#

import os
from pathlib import Path
import logging

import numpy as np
import wx

import fsl.utils.settings               as fslsettings
import fsl.data.image                   as fslimage
import fsleyes.actions                  as actions
import fsleyes_widgets.utils.status     as status
from fsleyes.views.orthopanel           import OrthoPanel
import fsleyes.controls.controlpanel    as ctrlpanel
import fsleyes_props                    as props

from fsleyes_plugin_mrs.views           import MRSView

log = logging.getLogger(__name__)


###########################################
# FSLFitTool - load results from fsl_mrsi #
###########################################
class FSLFitTool(actions.Action):
    """Load results as output from fsl_mrsi.
    Load and display fit in the MRSView display
    Add a FSLMRSResultsControl panel to the ortho view to allow
    easy loading of metabolite maps
    """
    def __init__(self, overlayList, displayCtx, frame):
        super().__init__(overlayList, displayCtx, self.__loadResults)
        self.frame = frame

    def __loadResults(self):
        """Show a dialog prompting the user for a directory to load.
        Subsequently interprets results structure, causes a FSLMRSResultsControl
        to be created and then load the fit, baseline, and residual overlays.
        """

        msg = 'Load fsl_mrs(i) fit directory'
        fromDir = fslsettings.read('loadSaveOverlayDir', os.getcwd())
        dlg = wx.DirDialog(wx.GetApp().GetTopWindow(),
                           message=msg,
                           defaultPath=fromDir,
                           style=wx.FD_OPEN)

        if dlg.ShowModal() != wx.ID_OK:
            return

        dirPath = Path(dlg.GetPath())
        errtitle = 'Error loading directory'
        errmsg = 'An error occurred while loading the fit directory.'
        with status.reportIfError(errtitle, errmsg, raiseError=False):
            # Steps:
            # 1. Look through the directory and identify metabolite names
            # and things that can be loaded
            self._identifyResults(dirPath)
            # 2. Create a panel to control the loading of the possible views
            self._createResultsPanel()
            # 3. Setup the ortho panel ready for the display
            self._set_up_ortho()
            # 4. Load the fit, baseline and residual into the MRS view.
            self._loadFit(dirPath)

    def _identifyResults(self, dir_path):
        """Identify the metabolites used and the images available.
        Store this information for use constructing the additional panel

        :param Path dir_path: Path selected by user in DirDialog window
        """
        # TODO modify this function to allow reading format from json file

        # print(f'Interpreting fit path {dir_path}')
        # List of metabolites
        self.metab_list = []
        for file in (dir_path / 'concs' / 'raw').glob('*.nii.gz'):
            while file.suffix in {'.nii', '.gz'}:
                file = file.with_suffix('')
            self.metab_list.append(file.name)

        # List of things that could be displayed
        self.display_options = {'conc-raw': dir_path / 'concs/raw/{}.nii.gz',
                                'conc-internal': dir_path / 'concs/internal/{}.nii.gz',
                                'conc-molarity': dir_path / 'concs/molarity/{}.nii.gz',
                                'conc-molality': dir_path / 'concs/molality/{}.nii.gz',
                                'uncertainties': dir_path / 'uncertainties/{}_sd.nii.gz',
                                'SNR': dir_path / 'qc/{}_snr.nii.gz',
                                'FWHM': dir_path / 'qc/{}_fwhm.nii.gz'}

    def _createResultsPanel(self):
        """Activate a FSLMRSResultsControl panel, update with the metablist and display options."""
        # Activate the panel
        ortho = self.frame.getView(OrthoPanel)
        if len(ortho) == 0:
            log.error('No Ortho panel present')
            return
        else:
            # Assume only 1 ortho panel
            ortho = ortho[0]

        if not ortho.isPanelOpen(FSLMRSResultsControl):
            ortho.togglePanel(FSLMRSResultsControl)

        # Update the properties
        ortho.getPanel(FSLMRSResultsControl).update_choices(self.metab_list, self.display_options)

    def _set_up_ortho(self):
        """Add colour bar to ortho panel."""
        ortho = self.frame.getView(OrthoPanel)
        if len(ortho) == 0:
            log.error('No Ortho panel present')
            return
        else:
            # Assume only 1 ortho panel
            ortho = ortho[0]

        orthoOpts = ortho.sceneOpts
        orthoOpts.showColourBar = True
        orthoOpts.colourBarLocation = 'left'
        orthoOpts.colourBarLabelSide = 'top-left'
        orthoOpts.labelSize = 10

    def _loadFit(self, dir_path):
        """Load the fit, baseline, and residual data from the fit subdir.
        Add to the overlayList and display in the MRSView panel.
        """
        def load_and_disp(file_name, lw, colour):
            # Load and add to the overlayList
            full_path = dir_path / 'fit' / f'{file_name}.nii.gz'
            if not full_path.exists():
                log.warning(f'{file_name} image not found in {full_path}, skipping.')
                return
            new_img = fslimage.Image(str(full_path))
            self.overlayList.append(new_img)

            # Loop through the viewPanels. If MRSView enable overlay, otherwise disable overlay
            for panel in self.frame.viewPanels:
                display = panel.displayCtx.getDisplay(self.overlayList[-1])
                if isinstance(panel, MRSView):
                    display.enabled = True

                    # Set colour etc.
                    # Get the data series
                    ps = panel.getDataSeries(self.overlayList[-1])
                    ps.lineStyle = '-'
                    ps.alpha = 1.0
                    ps.lineWidth = lw
                    ps.colour = colour
                else:
                    display.enabled = False

        # Load the fit scan
        load_and_disp('fit', 2, (1, 0, 0))
        # Load the baseline scan
        load_and_disp('baseline', 1, (0, 0.5, 0.5))
        # Load the fit scan
        load_and_disp('residual', 1, (0.2, 0.2, 0.2))


class FSLMRSResultsControl(ctrlpanel.SettingsPanel):
    """Control panel for the FSL-MRS results. Allows user to easily select overlays to plot
    """

    @staticmethod
    def title():
        """Overrides :meth:`.ControlMixin.title`. Returns a title to be used
        in FSLeyes menus.
        """
        return 'FSL-MRS Results'

    @staticmethod
    def defaultLayout():
        """Overrides :meth:`.ControlMixin.defaultLayout`. Returns arguments
        to be passed to :meth:`.ViewPanel.defaultLayout`.
        """
        return {'location': wx.BOTTOM}

    @staticmethod
    def supportedViews():
        """Overrides :meth:`.ControlMixin.supportedViews`. The
        ``FSLMRSResultsControl`` is only intended to be added to
        :class:`.OrthoPanel` views.
        """
        return [OrthoPanel]

    def __init__(self, parent, overlayList, displayCtx, viewPanel):
        """Create a ``FSLMRSResultsControl``.

        :arg parent:      The :mod:`wx` parent object.
        :arg overlayList: The :class:`.OverlayList` instance.
        :arg displayCtx:  The :class:`.DisplayContext` instance.
        :arg viewPanel:   The :class:`.ViewPanel` instance.
        :arg metabolites:   A list of possible metabolites.
        :arg overlay_options:   A dict of possible overlay types to load.
        """
        super().__init__(parent, overlayList, displayCtx, viewPanel)

        class propStore(props.HasProperties):
            """Class to store properties"""
            metabolite = props.Choice()
            overlay_type = props.Choice()
            replace = props.Boolean(default=True)

        self._propStore = propStore()
        self._overlay_types = None
        self._previous_overlay = None

        self.refreshWidgets()

    def destroy(self):
        """Must be called when this ``FSLMRSResultsControl`` is no
        longer needed. calls the
        :meth:`.SettingsPanel.destroy` method.
        """
        super().destroy()

    def _generateWidgets(self, group_name):
        '''Make the widgets required for the selection of overlays.'''

        widgetList = self.getWidgetList()

        widgets = []
        metab_sel = props.makeWidget(
                widgetList,
                self._propStore,
                'metabolite')
        widgetList.AddWidget(
                metab_sel,
                displayName='Metabolite',
                tooltip="Select metabolite",
                groupName=group_name)
        widgets.append(metab_sel)

        type_sel = props.makeWidget(
                widgetList,
                self._propStore,
                'overlay_type')
        widgetList.AddWidget(
                type_sel,
                displayName='Type',
                tooltip="Select plot type",
                groupName=group_name)
        widgets.append(type_sel)

        rep_select = props.makeWidget(
                widgetList,
                self._propStore,
                'replace')
        widgetList.AddWidget(
                rep_select,
                displayName='Replace?',
                tooltip="If selected new overlays replace old ones.",
                groupName=group_name)
        widgets.append(rep_select)

        self.__widgets = widgets

    def refreshWidgets(self):
        '''Refresh the widgets for the selection of overlays.
        Run after updating the choices (using update_choices).
        '''
        widgetList = self.getWidgetList()

        if widgetList.HasGroup('fsl_mrs_results'):
            widgetList.RemoveGroup('fsl_mrs_results')

        # Add listeners to the properties which will cause a
        # refresh of the Info Pannel.
        prop_metab = self._propStore.getProp('metabolite')
        prop_metab.addListener(
            self._propStore,
            'metabolite_choice_update',
            self._selected_result_change,
            overwrite=True)

        prop_ot = self._propStore.getProp('overlay_type')
        prop_ot.addListener(
            self._propStore,
            'metabolite_choice_update',
            self._selected_result_change,
            overwrite=True)

        widgetList.AddGroup(
            'fsl_mrs_results',
            'FSL-MRS Results ')

        self._generateWidgets('fsl_mrs_results')

    def update_choices(self, metabolites, overlay_types):
        '''Update the properties (metabolites and overlay types) in the panel.'''
        # Update the metabolite list
        metabolite = self._propStore.getProp('metabolite')
        metabolite.setChoices(metabolites, instance=self._propStore)
        # Update the overlay_types
        overlay_type = self._propStore.getProp('overlay_type')
        overlay_type.setChoices(list(overlay_types.keys()), instance=self._propStore)

        # Store the dictionary defining the types and formats of files.
        self._overlay_types = overlay_types

        # Refresh the widgets to update the GUI
        self.refreshWidgets()

    def _selected_result_change(self, *a):
        """Method called by listeners to load the selected overlay.
        If replace is true / selected then remove the previously loaded
        overlay.
        """
        if self._overlay_types is None:
            return

        full_path = str(self._overlay_types[self._propStore.overlay_type])\
            .format(self._propStore.metabolite)

        if (self._propStore.overlay_type == 'SNR' or self._propStore.overlay_type == 'FWHM')\
                and '+' in self._propStore.metabolite:
            log.info('SNR and FWHM are not defined for combined metabolites.')
            return

        if not Path(full_path).exists():
            log.warning(f'{full_path} image not found, skipping.')
            return

        # If the user has the replace checkbox selected remove any previously loaded
        # overlay
        if self._propStore.replace and self._previous_overlay is not None:
            # Remove previous overlay
            self.overlayList.remove(self._previous_overlay)

        # Load the new overlay
        new_img = fslimage.Image(str(full_path))
        self.overlayList.append(new_img)
        self._previous_overlay = new_img
        self._set_overlay_display(self._propStore.overlay_type)
        self.displayCtx.selectOverlay(new_img)

    def _set_overlay_display(self, type):
        '''Set the display options for the loaded overlay dependent on type.'''

        overlay = self.overlayList[-1]
        display = self.displayCtx.getDisplay(overlay)
        opts = self.displayCtx.getOpts(overlay)

        if 'conc-' in type:
            max_val = np.median(overlay.data[np.nonzero(overlay.data)])\
                 + 3 * np.std(overlay.data[np.nonzero(overlay.data)])
            opts.displayRange = [0.0, max_val]
            opts.cmap = 'hot'
            display.alpha = 67.0
        elif type == 'uncertainties':
            min_val = np.median(overlay.data[np.nonzero(overlay.data)])\
                - 2 * np.std(overlay.data[np.nonzero(overlay.data)])
            max_val = np.median(overlay.data[np.nonzero(overlay.data)])\
                + 2 * np.std(overlay.data[np.nonzero(overlay.data)])
            min_val = np.maximum(min_val, 0.0)
            max_val_clip = np.max(overlay.data[np.nonzero(overlay.data)])
            opts.linkLowRanges = False
            opts.displayRange = [min_val, max_val]
            opts.clippingRange = [0.0, max_val_clip]
            opts.cmap = 'cool'
            display.alpha = 67.0
        elif type == 'SNR':
            min_val = np.median(overlay.data[np.nonzero(overlay.data)])\
                - 2 * np.std(overlay.data[np.nonzero(overlay.data)])
            max_val = np.median(overlay.data[np.nonzero(overlay.data)])\
                + 2 * np.std(overlay.data[np.nonzero(overlay.data)])
            min_val = np.maximum(min_val, 0.0)
            max_val_clip = np.max(overlay.data[np.nonzero(overlay.data)])
            opts.linkLowRanges = False
            opts.displayRange = [min_val, max_val]
            opts.clippingRange = [0.0, max_val_clip]
            opts.cmap = 'red'
            display.alpha = 67.0
        elif type == 'FWHM':
            min_val = np.median(overlay.data[np.nonzero(overlay.data)])\
                - 2 * np.std(overlay.data[np.nonzero(overlay.data)])
            max_val = np.median(overlay.data[np.nonzero(overlay.data)])\
                + 2 * np.std(overlay.data[np.nonzero(overlay.data)])
            min_val = np.maximum(min_val, 0.0)
            max_val_clip = np.max(overlay.data[np.nonzero(overlay.data)])
            opts.linkLowRanges = False
            opts.displayRange = [min_val, max_val]
            opts.clippingRange = [0.0, max_val_clip]
            opts.cmap = 'blue'
            display.alpha = 67.0
