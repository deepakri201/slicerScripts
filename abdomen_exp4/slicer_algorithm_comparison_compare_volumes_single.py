# Modified from Steve Pieper's script: https://github.com/pieper/nnmouse/blob/main/mouse-review.py 
# And using Steve Pieper's code CompareVolumes: https://github.com/pieper/CompareVolumes/ 
# And using code from github repo https://github.com/deepakri201/slicerScripts/blob/main/synthsegViewSegAndGt.py
# 
# Red - Top left = our method (SynthSeg based)
# Gray (Slice4) - Top right = TotalSegmentatorMRI 
# Green - Bottom left = MRSegmentator
# Yellow - Bottom right = MRISegmentator-Abdomen
# 
# The ground truth is overlaid in each axial view as outlines. 
# 
# To run on Mac: 
# /Applications/Slicer\ 4.app/Contents/MacOS/Slicer --python-script /Users/dk422/git/slicerScripts/abdomen_exp4/slicer_algorithm_comparison_compare_volumes_single.py
# 
# Deepa Krishnaswamy 
# Brigham and Women's Hospital 
# July 2024 
##########################################################################################################

import os 

##############
### Inputs ### 
##############

# ### MR AMOS TRAIN 
# patientID = "amos_0557" # "amos_0580" # "amos_0583" # "amos_0557" # "amos_0507" # "amos_0508" # "amos_0518" # "amos_0600" # "amos_0541" # "amos_0580" # "amos_0596"
# BASE_IMAGES = "/Users/dk422/Documents/SynthSeg/validation/amos/processed/mr_images_train"
# BASE_LABELS = "/Users/dk422/Documents/SynthSeg/validation/amos/processed/mr_labels_train"
# BASE_RESULTS_SynthSeg = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/synthetic_results/amos22_mr_train/prediction_results_resampled/dice_100"
# BASE_RESULTS_TotalSegmentatorMRI = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/totalsegmri_results/amos22_mr_train/prediction_results_formatted"
# BASE_RESULTS_MRSegmentator = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/mrsegmentator_results/amos22_mr_train/prediction_results_formatted"
# BASE_RESULTS_MRISegmentatorAbdomen = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/mrisegmentatorabdomen_results/amos22_mr_train/prediction_results_formatted"

# ### CT AMOS TRAIN - SMALL
# patientID = "amos_0004"
# BASE_IMAGES = "/Users/dk422/Documents/SynthSeg/validation/amos/processed/ct_images_train"
# BASE_LABELS = "/Users/dk422/Documents/SynthSeg/validation/amos/processed/ct_labels_train"
# BASE_RESULTS_SynthSeg = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/synthetic_results/amos22_ct_train_small/prediction_results_resampled/dice_100"
# BASE_RESULTS_TotalSegmentatorMRI = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/totalsegmri_results/amos22_ct_train/prediction_results_formatted"
# BASE_RESULTS_MRSegmentator = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/mrsegmentator_results/amos22_ct_train/prediction_results_formatted"
# BASE_RESULTS_MRISegmentatorAbdomen = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/mrisegmentatorabdomen_results/amos22_ct_train_small/prediction_results_formatted"

# ### CHAOS MR 
# patientID = "mr_1_T1DUAL_INPHASE"
# BASE_IMAGES = "/Users/dk422/Documents/SynthSeg/validation/chaos/ready_synthseg_total_validation/mr/images_fixed_int16"
# BASE_LABELS = "/Users/dk422/Documents/SynthSeg/validation/chaos/ready_synthseg_total_validation/mr/labels"
# BASE_RESULTS_SynthSeg = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/synthetic_results/chaos_mr/prediction_results_resampled/dice_100"
# BASE_RESULTS_TotalSegmentatorMRI = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/totalsegmri_results/chaos_mr/prediction_results_formatted"
# BASE_RESULTS_MRSegmentator = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/mrsegmentator_results/chaos_mr/prediction_results_formatted"
# BASE_RESULTS_MRISegmentatorAbdomen = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/mrisegmentatorabdomen_results/chaos_mr/prediction_results_formatted"

### IDC CPTAC-UCEC
# patientID = "C3L-02403-1.3.6.1.4.1.14519.5.2.1.6450.2626.885627531366106480284196791991"
# patientID = "C3N-00860-1.3.6.1.4.1.14519.5.2.1.3320.3273.714694469302767764376208511501"
# patientID = "C3L-01248-1.3.6.1.4.1.14519.5.2.1.6450.2626.954193569206059855586529512707"
patientID = "C3N-00860-1.3.6.1.4.1.14519.5.2.1.3320.3273.714694469302767764376208511501"
BASE_IMAGES = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/idc_external_samples/cptac_ucec/images"
BASE_LABELS = ""
BASE_RESULTS_SynthSeg = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/synthetic_results/idc_cptac_ucec/prediction_results_resampled/dice_100"
BASE_RESULTS_TotalSegmentatorMRI = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/totalsegmri_results/idc_cptac_ucec/prediction_results_formatted"
BASE_RESULTS_MRSegmentator = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/mrsegmentator_results/idc_cptac_ucec/prediction_results_formatted"
BASE_RESULTS_MRISegmentatorAbdomen = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/mrisegmentatorabdomen_results/idc_cptac_ucec/prediction_results_formatted"


resultPath_SynthSeg = os.path.join(BASE_RESULTS_SynthSeg, patientID + '_synthseg.nii.gz')
resultPath_TotalSegmentatorMRI = os.path.join(BASE_RESULTS_TotalSegmentatorMRI, patientID + '.nii.gz')
resultPath_MRSegmentator = os.path.join(BASE_RESULTS_MRSegmentator, patientID + '_seg.nii.gz')
resultPath_MRISegmentatorAbdomen = os.path.join(BASE_RESULTS_MRISegmentatorAbdomen, patientID + '.nii.gz')

##################
### Parameters ### 
##################

color_table_filename = '/Users/dk422/git/slicerScripts/color_table_NLST_TotalSegmentator.ctbl'

##############
### Set up ### 
##############

###### Gt and pred have different labels, color the labels according to the same id #####

resultIndex = 0
labelNode = None
volumeNode = None 
segNodes = []

print('BASE_IMAGES: ' + str(BASE_IMAGES))
print('BASE_LABELS: ' + str(BASE_LABELS))
print('BASE_RESULTS_SynthSeg: ' + str(BASE_RESULTS_SynthSeg))
print('BASE_RESULTS_TotalSegmentatorMRI: ' + str(BASE_RESULTS_TotalSegmentatorMRI))
print('BASE_RESULTS_MRSegmentator: ' + str(BASE_RESULTS_MRSegmentator))
print('BASE_RESULTS_MRISegmentatorAbdomen: ' + str(BASE_RESULTS_MRISegmentatorAbdomen))

print('patientID: ' + str(patientID))

print('resultPath_SynthSeg: ' + str(resultPath_SynthSeg))
print('resultPath_TotalSegmentatorMRI: ' + str(resultPath_TotalSegmentatorMRI))
print('resultPath_MRSegmentator: ' + str(resultPath_MRSegmentator))
print('resultPath_MRISegmentatorAbdomen: ' + str(resultPath_MRISegmentatorAbdomen))

##################
### Imports ### 
##################

import glob
import os
import io
import requests

import os, string
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
# import CompareVolumes

try:
  import pandas as pd
except ModuleNotFoundError:
  if slicer.util.confirmOkCancelDisplay("This module requires 'pandas' Python package. Click OK to install it now."):
    slicer.util.pip_install("pandas")
    import pandas as pd

############################################################################
### Here I modify the CompareVolumes Logic from Steve, by adding in ###
### the option to display segmentation nodes in each of the slice views ###
############################################################################

class CompareVolumesLogicDK(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget
    """
    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self.sliceViewItemPattern = """
            <item><view class="vtkMRMLSliceNode" singletontag="{viewName}">
            <property name="orientation" action="default">{orientation}</property>
            <property name="viewlabel" action="default">{viewName}</property>
            <property name="viewcolor" action="default">{color}</property>
            </view></item>
            """
        # use a nice set of colors
        self.colors = slicer.util.getNode('GenericColors')
        self.lookupTable = self.colors.GetLookupTable()

    def assignLayoutDescription(self,layoutDescription):
        """assign the xml to the user-defined layout slot"""
        layoutNode = slicer.util.getNode('*LayoutNode*')
        if layoutNode.IsLayoutDescription(layoutNode.SlicerLayoutUserView):
            layoutNode.SetLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
        else:
            layoutNode.AddLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
        layoutNode.SetViewArrangement(layoutNode.SlicerLayoutUserView)

    def viewerPerVolume(self,volumeNodes=None,background=None,segNodes=None,label=None,viewNames=[],layout=None,orientation='Axial',opacity=0.5):
        """ Load each volume in the scene into its own
        slice viewer and link them all together.
        If background is specified, put it in the background
        of all viewers and make the other volumes be the
        forground.  If label is specified, make it active as
        the label layer of all viewers.
        Return a map of slice nodes indexed by the view name (given or generated).
        Opacity applies only when background is selected.
        """
        import math

        if not volumeNodes:
            volumeNodes = list(slicer.util.getNodes('*VolumeNode*').values())

        if len(volumeNodes) == 0:
            return

        volumeCount = len(volumeNodes)
        volumeCountSqrt = math.sqrt(volumeCount)
        if layout:
            rows = layout[0]
            columns = layout[1]
        elif volumeCountSqrt == math.floor(volumeCountSqrt):
            rows = int(volumeCountSqrt)
            columns = int(volumeCountSqrt)
        else:
            # make an array with wide screen aspect ratio
            # - e.g. 3 volumes in 3x1 grid
            # - 5 volumes 3x2 with only two volumes in second row
            c = 1.5 * volumeCountSqrt
            columns = math.floor(c)
            if (c != columns) and (volumeCount % columns != 0):
                columns += 1
            if columns > volumeCount:
                columns = volumeCount
                r = volumeCount / columns
                rows = math.floor(r)
            if r != rows:
                rows += 1

        #
        # construct the XML for the layout
        # - one viewer per volume
        # - default orientation as specified
        #
        actualViewNames = []
        index = 1
        layoutDescription = ''
        layoutDescription += '<layout type="vertical">\n'
        for row in range(int(rows)):
            layoutDescription += ' <item> <layout type="horizontal">\n'
            for column in range(int(columns)):
                try:
                    viewName = viewNames[index-1]
                except IndexError:
                    viewName = '%d_%d' % (row,column)
                rgb = [int(round(v*255)) for v in self.lookupTable.GetTableValue(index)[:-1]]
                color = '#%0.2X%0.2X%0.2X' % tuple(rgb)
                layoutDescription += self.sliceViewItemPattern.format(viewName=viewName,orientation=orientation,color=color)
                actualViewNames.append(viewName)
                index += 1
            layoutDescription += '</layout></item>\n'
        layoutDescription += '</layout>'
        self.assignLayoutDescription(layoutDescription)

        # let the widgets all decide how big they should be
        slicer.app.processEvents()

        # put one of the volumes into each view, or none if it should be blank
        sliceNodesByViewName = {}
        layoutManager = slicer.app.layoutManager()
        for index in range(len(actualViewNames)):
            viewName = actualViewNames[index]
            try:
                volumeNodeID = volumeNodes[index].GetID()
            except IndexError:
                volumeNodeID = ""

            sliceWidget = layoutManager.sliceWidget(viewName)
            compositeNode = sliceWidget.mrmlSliceCompositeNode()
            if background:
                compositeNode.SetBackgroundVolumeID(background.GetID())
                compositeNode.SetForegroundVolumeID(volumeNodeID)
                compositeNode.SetForegroundOpacity(opacity)
            else:
                compositeNode.SetBackgroundVolumeID(volumeNodeID)
                compositeNode.SetForegroundVolumeID("")

            if label:
                compositeNode.SetLabelVolumeID(label.GetID())
            else:
                compositeNode.SetLabelVolumeID("")

            if segNodes: 
                segmentationDisplayNode = segNodes[index].GetDisplayNode()
                sliceNode = 'vtkMRMLSliceNode' + viewName 
                # sliceNode = viewName
                segmentationDisplayNode.SetDisplayableOnlyInView(sliceNode)
            

            sliceNode = sliceWidget.mrmlSliceNode()
            sliceNode.SetOrientation(orientation)
            sliceNodesByViewName[viewName] = sliceNode
        return sliceNodesByViewName 

    def rotateToVolumePlanes(self, referenceVolume):
        sliceNodes = slicer.util.getNodes('vtkMRMLSliceNode*')
        for name, node in list(sliceNodes.items()):
            node.RotateToVolumePlane(referenceVolume)
        # snap to IJK to try and avoid rounding errors
        sliceLogics = slicer.app.layoutManager().mrmlSliceLogics()
        numLogics = sliceLogics.GetNumberOfItems()
        for n in range(numLogics):
            l = sliceLogics.GetItemAsObject(n)
            l.SnapSliceOffsetToIJK()

    def zoom(self,factor,sliceNodes=None):
        """Zoom slice nodes by factor.
        factor: "Fit" or +/- amount to zoom
        sliceNodes: list of slice nodes to change, None means all.
        """
        if not sliceNodes:
            sliceNodes = slicer.util.getNodes('vtkMRMLSliceNode*')
        layoutManager = slicer.app.layoutManager()
        for sliceNode in list(sliceNodes.values()):
            if factor == "Fit":
                sliceWidget = layoutManager.sliceWidget(sliceNode.GetLayoutName())
            if sliceWidget:
                sliceWidget.sliceLogic().FitSliceToAll()
            else:
                newFOVx = sliceNode.GetFieldOfView()[0] * factor
                newFOVy = sliceNode.GetFieldOfView()[1] * factor
                newFOVz = sliceNode.GetFieldOfView()[2]
                sliceNode.SetFieldOfView( newFOVx, newFOVy, newFOVz )
                sliceNode.UpdateMatrices()

#######################
### The actual code ###
#######################

def load():

    colorNode = slicer.util.loadColorTable(color_table_filename)

    global labelNode, volumeNode, segNodes
    for node in [labelNode, volumeNode]:
        if node:
            slicer.mrmlScene.RemoveNode(node)
    for node in segNodes: 
        if node: 
            slicer.mrmlScene.RemoveNode(node)

    ### Load the background volume for all 4 slice views ### 
    volumeFileName = os.path.join(BASE_IMAGES, patientID + ".nii.gz")
    print('volumeFileName: ' + str(volumeFileName))
    volumeNode = slicer.util.loadVolume(volumeFileName, properties={"singleFile": True})
    volumeNodes = [volumeNode] * 4 
   
    ### Load the segmentations for each of the 4 slice views ### 
    # Load
    resultNode_SynthSeg = slicer.util.loadSegmentation(resultPath_SynthSeg, {'colorNodeID': colorNode.GetID()})
    resultNode_TotalSegmentatorMRI = slicer.util.loadSegmentation(resultPath_TotalSegmentatorMRI, {'colorNodeID': colorNode.GetID()})
    resultNode_MRSegmentator = slicer.util.loadSegmentation(resultPath_MRSegmentator, {'colorNodeID': colorNode.GetID()})
    resultNode_MRISegmentatorAbdomen = slicer.util.loadSegmentation(resultPath_MRISegmentatorAbdomen, {'colorNodeID': colorNode.GetID()})
    segNodes = [] 
    segNodes.append(resultNode_SynthSeg)
    segNodes.append(resultNode_TotalSegmentatorMRI)
    segNodes.append(resultNode_MRSegmentator)
    segNodes.append(resultNode_MRISegmentatorAbdomen)

    ### Load the ground truth label - display as thick outline in each of the views ### 
    # Load
    if (BASE_LABELS):
        labelFileName = os.path.join(BASE_LABELS, patientID + ".nii.gz")
        print('labelFileName: ' + str(labelFileName))
        labelNode = slicer.util.loadSegmentation(labelFileName, {'colorNodeID': colorNode.GetID()})

    # cvLogic = CompareVolumes.CompareVolumesLogic()
    cvLogic = CompareVolumesLogicDK()
    # cvLogic.viewerPerVolume(volumeNodes, background=volumeNodes[0], label=labelNode,
    #                         layout=[2,2],viewNames=['Ours - SynthSeg-based', 'TotalSegmentatorMRI', 'MRSegmentator', 'MRISegmentator-Abdomen'],
    #                         orientation='Axial')

    if (BASE_LABELS):
        cvLogic.viewerPerVolume(volumeNodes=volumeNodes, background=volumeNodes[0], segNodes=segNodes, label=labelNode,
                                layout=[2,2],viewNames=['Ours - SynthSeg-based', 'TotalSegmentatorMRI', 'MRSegmentator', 'MRISegmentator-Abdomen'],
                                orientation='Axial')
    else: 
        cvLogic.viewerPerVolume(volumeNodes=volumeNodes, background=volumeNodes[0], segNodes=segNodes,
                        layout=[2,2],viewNames=['Ours - SynthSeg-based', 'TotalSegmentatorMRI', 'MRSegmentator', 'MRISegmentator-Abdomen'],
                        orientation='Axial')

    # Display labelmap node 
    if (BASE_LABELS):
        labelNode.GetDisplayNode().SetAllSegmentsOpacity2DFill(0.0)
        labelNode.GetDisplayNode().SetAllSegmentsOpacity2DOutline(1.0)
        labelNode.GetDisplayNode().SetSliceIntersectionThickness(3)

    # Now link all the slice views 
    # https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html#set-all-slice-views-linked-by-default 
    # Set linked slice views  in all existing slice composite nodes and in the default node

    sliceCompositeNodes = slicer.util.getNodesByClass("vtkMRMLSliceCompositeNode")
    for sliceCompositeNode in sliceCompositeNodes:
        sliceCompositeNode.SetLinkedControl(True)

    # sliceCompositeNodes = slicer.util.getNodesByClass("vtkMRMLSliceCompositeNode")
    # defaultSliceCompositeNode = slicer.mrmlScene.GetDefaultNodeByClass("vtkMRMLSliceCompositeNode")
    # if not defaultSliceCompositeNode:
    #     defaultSliceCompositeNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSliceCompositeNode")
    #     defaultSliceCompositeNode.UnRegister(None)  # CreateNodeByClass is factory method, need to unregister the result to prevent memory leaks
    #     slicer.mrmlScene.AddDefaultNode(defaultSliceCompositeNode)
    # sliceCompositeNodes.append(defaultSliceCompositeNode)
    # for sliceCompositeNode in sliceCompositeNodes:
    #     sliceCompositeNode.SetLinkedControl(True)




# button = qt.QPushButton("Next")
# button.connect("clicked()", load)
# button.show()

load()

