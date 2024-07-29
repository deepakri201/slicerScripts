# Modified from Steve Pieper's script: https://github.com/pieper/nnmouse/blob/main/mouse-review.py
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
# /Applications/Slicer\ 4.app/Contents/MacOS/Slicer --python-script /Users/dk422/git/slicerScripts/abdomen_exp4/slicer_algorithm_comparison.py
# 
# To run in Windows: 
# cd to C:\Users\deepa\AppData\Local\slicer.org\Slicer 5.6.1
# Slicer.exe --python-script "D://deepa//Slicer//SynthSegViewSegAndGt//synthsegViewSegAndGt.py" # --no-splash  --no-main-window
# Slicer.exe --python-script "C://Users//deepa//git//slicerScripts//synthsegViewSegAndGt.py"
# 
# 
# Deepa Krishnaswamy 
# Brigham and Women's Hospital 
# July 2024 
##########################################################################################################

##################
### Parameters ### 
##################

color_table_filename = '/Users/dk422/git/slicerScripts/color_table_Slicer.ctbl'

##################
### Imports ### 
##################

import glob
import os
import io
import requests

try:
  import pandas as pd
except ModuleNotFoundError:
  if slicer.util.confirmOkCancelDisplay("This module requires 'pandas' Python package. Click OK to install it now."):
    slicer.util.pip_install("pandas")
    import pandas as pd

##################
### Set up ### 
##################

###### Gt and pred have different labels, color the labels according to the same id #####

### MR AMOS TRAIN 
BASE_IMAGES = "/Users/dk422/Documents/SynthSeg/validation/amos/processed/mr_images_train"
BASE_LABELS = "/Users/dk422/Documents/SynthSeg/validation/amos/processed/mr_labels_train"
# BASE_RESULTS = "/Users/dk422/Documents/SynthSeg/staple/amos22_mr_train/consensus"
BASE_RESULTS_SynthSeg = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/synthetic_results/amos22_mr_train/prediction_results_resampled/dice_100"
BASE_RESULTS_TotalSegmentatorMRI = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/totalsegmri_results/amos22_mr_train/prediction_results_formatted"
BASE_RESULTS_MRSegmentator = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/mrsegmentator_results/amos22_mr_train/prediction_results_formatted"
BASE_RESULTS_MRISegmentatorAbdomen = "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/mrisegmentatorabdomen_results/amos22_mr_train/prediction_results_formatted"

resultIndex = 0
labelNode = None
resultNode = None
volumeNode = None
labelMapNode = None
resultNodeList = [] 

resultPaths_SynthSeg = sorted(glob.glob(f"{BASE_RESULTS_SynthSeg}/*.nii.gz")) # amos_0507_synthseg.nii.gz
resultPaths_TotalSegmentatorMRI = sorted(glob.glob(f"{BASE_RESULTS_TotalSegmentatorMRI}/*.nii.gz")) # amos_0507.nii.gz
resultPaths_MRSegmentator = sorted(glob.glob(f"{BASE_RESULTS_MRSegmentator}/*.nii.gz")) # amos_0507_seg.nii.gz
resultPaths_MRISegmentatorAbdomen = sorted(glob.glob(f"{BASE_RESULTS_MRISegmentatorAbdomen}/*.nii.gz")) # amos_0507.nii.gz

print('BASE_IMAGES: ' + str(BASE_IMAGES))
print('BASE_LABELS: ' + str(BASE_LABELS))
print('BASE_RESULTS_SynthSeg: ' + str(BASE_RESULTS_SynthSeg))
print('BASE_RESULTS_TotalSegmentatorMRI: ' + str(BASE_RESULTS_TotalSegmentatorMRI))
print('BASE_RESULTS_MRSegmentator: ' + str(BASE_RESULTS_MRSegmentator))
print('BASE_RESULTS_MRISegmentatorAbdomen: ' + str(BASE_RESULTS_MRISegmentatorAbdomen))

# # resultPaths = glob.glob(f"{BASE_RESULTS}/*.nii.gz")
# # folder for each patient now. 
# resultPaths = glob.glob(f"{BASE_RESULTS}/*")
# resultPaths = sorted(resultPaths)

# print('BASE_IMAGES: ' + str(BASE_IMAGES))
# print('BASE_LABELS: ' + str(BASE_LABELS))
# print('BASE_RESULTS: ' + str(BASE_RESULTS))
# print('resultPaths: ' + str(resultPaths))

def load():

    colorNode = slicer.util.loadColorTable(color_table_filename)

    # Create and configure the layout
    layoutManager = slicer.app.layoutManager()
    layoutNode = slicer.app.layoutManager().layoutLogic().GetLayoutNode()
    layoutNode.SetViewArrangement(slicer.vtkMRMLLayoutNode.SlicerLayoutTwoOverTwoView)

    # Set the slice views to be red (axial)
    layoutManager.sliceWidget("Red").mrmlSliceNode().SetOrientationToAxial()
    layoutManager.sliceWidget("Red").mrmlSliceCompositeNode().SetBackgroundVolumeID(None)
    layoutManager.sliceWidget("Slice4").mrmlSliceNode().SetOrientationToAxial()
    layoutManager.sliceWidget("Slice4").mrmlSliceCompositeNode().SetBackgroundVolumeID(None)
    layoutManager.sliceWidget("Green").mrmlSliceNode().SetOrientationToAxial()
    layoutManager.sliceWidget("Green").mrmlSliceCompositeNode().SetBackgroundVolumeID(None)
    layoutManager.sliceWidget("Yellow").mrmlSliceNode().SetOrientationToAxial()
    layoutManager.sliceWidget("Yellow").mrmlSliceCompositeNode().SetBackgroundVolumeID(None)

    # Adjust the view names to fit your setup
    layoutManager.sliceWidget("Red").setMRMLScene(slicer.mrmlScene)
    layoutManager.sliceWidget("Slice4").setMRMLScene(slicer.mrmlScene)
    layoutManager.sliceWidget("Green").setMRMLScene(slicer.mrmlScene)
    layoutManager.sliceWidget("Yellow").setMRMLScene(slicer.mrmlScene)

    global resultIndex, labelNode, labelMapNode, volumeNode, resultNode, resultNodeList, resultPaths
    for node in [labelNode, labelMapNode, volumeNode, resultNode]:
        if node:
            slicer.mrmlScene.RemoveNode(node)
    for node in resultNodeList: 
        if node: 
            slicer.mrmlScene.RemoveNode(node)

    resultPath_SynthSeg = resultPaths_SynthSeg[resultIndex]
    resultPath_TotalSegmentatorMRI = resultPaths_TotalSegmentatorMRI[resultIndex]
    resultPath_MRSegmentator = resultPaths_MRSegmentator[resultIndex]
    resultPath_MRISegmentatorAbdomen = resultPaths_MRISegmentatorAbdomen[resultIndex]
    print('resultPath_SynthSeg: ' + str(resultPath_SynthSeg))
    print('resultPath_TotalSegmentatorMRI: ' + str(resultPath_TotalSegmentatorMRI))
    print('resultPath_MRSegmentator: ' + str(resultPath_MRSegmentator))
    print('resultPath_MRISegmentatorAbdomen: ' + str(resultPath_MRISegmentatorAbdomen))
    resultIndex += 1

    patientID = os.path.basename(resultPath_TotalSegmentatorMRI) # because this one is just amos_0000.nii.gz with no suffix. 
    patientID = os.path.splitext(os.path.splitext(patientID)[0])[0]
    print('patientID: ' + str(patientID))

    ### Load the background volume for all 4 slice views ### 
    volumeFileName = os.path.join(BASE_IMAGES, patientID + ".nii.gz")
    print('volumeFileName: ' + str(volumeFileName))
    volumeNode = slicer.util.loadVolume(volumeFileName, properties={"singleFile": True})
    # Assign 
    layoutManager.sliceWidget("Red").mrmlSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())
    layoutManager.sliceWidget("Red").mrmlSliceNode().SetOrientationToAxial()
    layoutManager.sliceWidget("Red").sliceController().fitSliceToBackground()
    layoutManager.sliceWidget("Slice4").mrmlSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())
    layoutManager.sliceWidget("Slice4").mrmlSliceNode().SetOrientationToAxial()
    layoutManager.sliceWidget("Slice4").sliceController().fitSliceToBackground()
    layoutManager.sliceWidget("Green").mrmlSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())
    layoutManager.sliceWidget("Green").mrmlSliceNode().SetOrientationToAxial()
    layoutManager.sliceWidget("Green").sliceController().fitSliceToBackground()
    layoutManager.sliceWidget("Yellow").mrmlSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())
    layoutManager.sliceWidget("Yellow").mrmlSliceNode().SetOrientationToAxial()
    layoutManager.sliceWidget("Yellow").sliceController().fitSliceToBackground()

    ### Load the segmentations for each of the 4 slice views ### 
    # Load
    resultNode_SynthSeg = slicer.util.loadSegmentation(resultPath_SynthSeg, {'colorNodeID': colorNode.GetID()})
    resultNode_TotalSegmentatorMRI = slicer.util.loadSegmentation(resultPath_TotalSegmentatorMRI, {'colorNodeID': colorNode.GetID()})
    resultNode_MRSegmentator = slicer.util.loadSegmentation(resultPath_MRSegmentator, {'colorNodeID': colorNode.GetID()})
    resultNode_MRISegmentatorAbdomen = slicer.util.loadSegmentation(resultPath_MRISegmentatorAbdomen, {'colorNodeID': colorNode.GetID()})

    viewNames = ['Red', 'Slice4', 'Green', 'Yellow']
    segmentationNodes = [resultNode_SynthSeg, 
                         resultNode_TotalSegmentatorMRI, 
                         resultNode_MRSegmentator, 
                         resultNode_MRISegmentatorAbdomen]

    # Load MR volume into each view
    for viewName in viewNames:
        sliceWidget = layoutManager.sliceWidget(viewName)
        sliceLogic = sliceWidget.sliceLogic()
        sliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())

    # # Function to set segmentation display in a specific view
    # def setSegmentationVisibilityInView(segmentationNode, viewName):
    #     displayNode = segmentationNode.GetDisplayNode()
    #     if not displayNode:
    #         segmentationNode.CreateDefaultDisplayNodes()
    #         displayNode = segmentationNode.GetDisplayNode()
    #     sliceViewNode = slicer.mrmlScene.GetNodeByID(viewName + 'View')
    #     displayNode.RemoveAllViewNodeIDs()
    #     displayNode.AddViewNodeID(sliceViewNode)

    # # Ensure each segmentation is visible only in its specific view
    # for i, viewName in enumerate(viewNames):
    #     setSegmentationVisibilityInView(segmentationNodes[i], viewName)

    # # Adjust opacity if needed (e.g., set the foreground opacity to 0.5)
    # for viewName in viewNames:
    #     sliceWidget = layoutManager.sliceWidget(viewName)
    #     sliceCompositeNode = sliceWidget.sliceLogic().GetSliceCompositeNode()
    #     sliceCompositeNode.SetForegroundOpacity(0.5)

    # Function to set segmentation display in a specific view
    def setSegmentationVisibility(segmentationNode, viewName, visibility):
        displayNode = segmentationNode.GetDisplayNode()
        if not displayNode:
            segmentationNode.CreateDefaultDisplayNodes()
            displayNode = segmentationNode.GetDisplayNode()
        sliceViewNode = slicer.mrmlScene.GetNodeByID(viewName + 'View')
        # displayNode.AddViewNodeID(sliceViewNode.GetID())
        displayNode.RemoveAllViewNodeIDs()
        displayNode.AddViewNodeID(sliceViewNode)
        displayNode.SetVisibility(visibility)

    # Set each segmentation to be visible in its specific view only
    for i, viewName in enumerate(viewNames):
        for j, segmentationNode in enumerate(segmentationNodes):
            visibility = (i == j)
            setSegmentationVisibility(segmentationNode, viewName, visibility)

    # Adjust opacity if needed (e.g., set the foreground opacity to 0.5)
    for viewName in viewNames:
        sliceWidget = layoutManager.sliceWidget(viewName)
        sliceCompositeNode = sliceWidget.sliceLogic().GetSliceCompositeNode()
        sliceCompositeNode.SetForegroundOpacity(0.5)

    # # Function to display only the specified segmentation in a view
    # def displaySegmentationInView(segmentationNode, volumeNode, viewID):
    #     displayNode = segmentationNode.GetDisplayNode()
    #     displayNode.SetVisibility(1)
    #     for otherViewID in viewIDs:
    #         if otherViewID != viewID:
    #             sliceWidget = layoutManager.sliceWidget(otherViewID)
    #             sliceLogic = sliceWidget.sliceLogic()
    #             sliceCompositeNode = sliceLogic.GetSliceCompositeNode()
    #             sliceCompositeNode.SetBackgroundVolumeID(volumeNode.GetID())
    #             sliceCompositeNode.SetLabelVolumeID(None)
    #     # displayNode.SetVisibility2DFill(True)
    #     # displayNode.SetVisibility2DOutline(True)
    #     segmentationNode.CreateDefaultDisplayNodes()

    ### Load the ground truth label - display as thick outline in each of the views ### 
    # Load
    labelFileName = os.path.join(BASE_LABELS, patientID + ".nii.gz")
    print('labelFileName: ' + str(labelFileName))
    labelNode = slicer.util.loadSegmentation(labelFileName, {'colorNodeID': colorNode.GetID()})
    # Display 
    labelNode.GetDisplayNode().SetAllSegmentsOpacity2DFill(0.0)
    labelNode.GetDisplayNode().SetAllSegmentsOpacity2DOutline(1.0)
    labelNode.GetDisplayNode().SetSliceIntersectionThickness(3)


button = qt.QPushButton("Next")
button.connect("clicked()", load)
button.show()

load()