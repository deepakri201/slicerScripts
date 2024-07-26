# Modified from Steve Pieper's script: https://github.com/pieper/nnmouse/blob/main/mouse-review.py
# And using code from github repo https://github.com/deepakri201/slicerScripts/blob/main/synthsegViewSegAndGt.py
# 
# Left view: MR image and ground truth label on top 
# Right view: MR image and each of the consensus segmentations - will have to toggle 
# 
# To run on Mac: 
# /Applications/Slicer\ 4.app/Contents/MacOS/Slicer --python-script /Users/dk422/Documents/SynthSeg/staple/slicer_staple_amos.py
# 
# 
# To run: 
# cd to C:\Users\deepa\AppData\Local\slicer.org\Slicer 5.6.1
# Slicer.exe --python-script "D://deepa//Slicer//SynthSegViewSegAndGt//synthsegViewSegAndGt.py" # --no-splash  --no-main-window
# Slicer.exe --python-script "C://Users//deepa//git//slicerScripts//synthsegViewSegAndGt.py"

# 
# Deepa Krishnaswamy 
# Brigham and Women's Hospital 
# July 2024 
##########################################################################################################

##################
### Parameters ### 
##################

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
BASE_RESULTS = "/Users/dk422/Documents/SynthSeg/staple/amos22_mr_train/consensus"

resultIndex = 0
labelNode = None
resultNode = None
volumeNode = None
labelMapNode = None
resultNodeList = [] 

# resultPaths = glob.glob(f"{BASE_RESULTS}/*.nii.gz")
# folder for each patient now. 
resultPaths = glob.glob(f"{BASE_RESULTS}/*")
resultPaths = sorted(resultPaths)

print('BASE_IMAGES: ' + str(BASE_IMAGES))
print('BASE_LABELS: ' + str(BASE_LABELS))
print('BASE_RESULTS: ' + str(BASE_RESULTS))
print('resultPaths: ' + str(resultPaths))

def load():

    # Create and configure the layout
    layoutManager = slicer.app.layoutManager()
    layoutNode = slicer.app.layoutManager().layoutLogic().GetLayoutNode()
    layoutNode.SetViewArrangement(slicer.vtkMRMLLayoutNode.SlicerLayoutSideBySideView)

    # Set the slice views to be red (axial)
    layoutManager.sliceWidget("Red").mrmlSliceNode().SetOrientationToAxial()
    layoutManager.sliceWidget("Red").mrmlSliceCompositeNode().SetBackgroundVolumeID(None)
    layoutManager.sliceWidget("Yellow").mrmlSliceNode().SetOrientationToAxial()
    layoutManager.sliceWidget("Yellow").mrmlSliceCompositeNode().SetBackgroundVolumeID(None)

    # Adjust the view names to fit your setup
    layoutManager.sliceWidget("Red").setMRMLScene(slicer.mrmlScene)
    layoutManager.sliceWidget("Yellow").setMRMLScene(slicer.mrmlScene)

    # global resultIndex, labelNode, volumeNode, resultNode, resultPaths
    # for node in [labelNode, volumeNode, resultNode]:
    #     if node:
    #         slicer.mrmlScene.RemoveNode(node)

    global resultIndex, labelNode, labelMapNode, volumeNode, resultNode, resultNodeList, resultPaths
    for node in [labelNode, labelMapNode, volumeNode, resultNode]:
        if node:
            slicer.mrmlScene.RemoveNode(node)
    for node in resultNodeList: 
        if node: 
            slicer.mrmlScene.RemoveNode(node)

    resultPath = resultPaths[resultIndex]
    print('resultPath: ' + str(resultPath))
    resultIndex += 1
    # resultNode = slicer.util.loadSegmentation(resultPath)
    # need to load all segmentations from the folder 
    resultPathSegs = glob.glob(f"{resultPath}/*.nii.gz")
    resultPathSegsNum = len(resultPathSegs)
    print('resultPathSegs: ' + str(resultPathSegs))
    print('resultPathSegsNum: ' + str(resultPathSegsNum))

    # patientID = resultPath.split("\\")[-1]
    patientID = os.path.basename(resultPath)
    print('patientID: ' + str(patientID))

    ### Load the background volume for both of the Red and Red1 slices ### 
    # volumeFileName = os.path.join(BASE_IMAGES, patientID)
    volumeFileName = os.path.join(BASE_IMAGES, patientID + ".nii.gz")
    print('volumeFileName: ' + str(volumeFileName))
    volumeNode = slicer.util.loadVolume(volumeFileName, properties={"singleFile": True})
    # Assign 
    layoutManager.sliceWidget("Red").mrmlSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())
    layoutManager.sliceWidget("Yellow").mrmlSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())
    layoutManager.sliceWidget("Yellow").mrmlSliceNode().SetOrientationToAxial()

    ### Load the label gt in the right view as a segmentation ### 
    # labelFileName = os.path.join(BASE_LABELS,patientID)
    labelFileName = os.path.join(BASE_LABELS, patientID + ".nii.gz")
    print('labelFileName: ' + str(labelFileName))
    labelNode = slicer.util.loadSegmentation(labelFileName)
    labelDisplayNode = labelNode.GetDisplayNode()
    # labelDisplayNode.SetVisibility2DFill(False) 
    # labelDisplayNode.SetAllSegmentsOpacity2DOutline(True)
    labelDisplayNode.SetSliceIntersectionOpacity(0.5)

    # layoutManager.sliceWidget("Yellow").mrmlSliceCompositeNode().SetLabelVolumeID(labelNode.GetID())
    # layoutManager.sliceWidget("Red").mrmlSliceCompositeNode().SetLabelVolumeID("") 

    # Convert the segmentation to a label map node 
    labelMapNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(labelNode, labelMapNode, volumeNode)
    # And then set in the individual views 
    layoutManager.sliceWidget("Yellow").mrmlSliceCompositeNode().SetLabelVolumeID(labelMapNode.GetID())
    ### Fix this after ### - want to display the outlines, not filled. 
    # labelMapNode.GetDisplayNode().SetAllSegmentsOpacity2DFill(0.0)
    # labelMapNode.GetDisplayNode().SetAllSegmentsOpacity2DOutline(1.0)
    # labelMapNode.GetDisplayNode().SetSliceIntersectionThickness(3)
    layoutManager.sliceWidget("Red").mrmlSliceCompositeNode().SetLabelVolumeID("")
    # Now that we have the labelmap node, can remove the segmentation node 
    slicer.mrmlScene.RemoveNode(labelNode)

    ### Now add the consensus, one for each region, to the left red view ###

    # Set the visibility to be off for all, 
    # Except for 1st one, toggle on for the foreground 
    # Set the opacity, maybe change the colormap
    resultNodeList = []
    for n in range(0, resultPathSegsNum): 
        resultPathSeg = resultPathSegs[n]
        resultNode = slicer.util.loadVolume(resultPathSeg)
        resultNodeList.append(resultNode)
        # Set background again
        layoutManager.sliceWidget("Red").mrmlSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())
        layoutManager.sliceWidget("Red").mrmlSliceNode().SetOrientationToAxial()
        layoutManager.sliceWidget("Yellow").mrmlSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())
        layoutManager.sliceWidget("Yellow").mrmlSliceNode().SetOrientationToAxial()
        layoutManager.sliceWidget("Red").sliceController().fitSliceToBackground()
        layoutManager.sliceWidget("Yellow").sliceController().fitSliceToBackground()
        # Set foreground 
        layoutManager.sliceWidget("Red").mrmlSliceCompositeNode().SetForegroundVolumeID(resultNode.GetID())
        layoutManager.sliceWidget("Yellow").mrmlSliceCompositeNode().SetForegroundVolumeID("")
        # Set label in yellow view 
        layoutManager.sliceWidget("Yellow").mrmlSliceCompositeNode().SetLabelVolumeID(labelMapNode.GetID())
        # Set visibility for all nodes except for 1st one 
        if n==0: 
            resultNode.GetDisplayNode().SetVisibility(True)
            # Set the colormap 
            colorNode = slicer.util.getNode("HotToColdRainbow")
            resultNode.GetDisplayNode().SetAndObserveColorNodeID(colorNode.GetID())
            layoutManager.sliceWidget("Red").mrmlSliceCompositeNode().SetForegroundOpacity(0.5)
        if n>0: 
            resultNode.GetDisplayNode().SetVisibility(False)
            # Set the colormap 
            colorNode = slicer.util.getNode("HotToColdRainbow")
            resultNode.GetDisplayNode().SetAndObserveColorNodeID(colorNode.GetID())
            layoutManager.sliceWidget("Red").mrmlSliceCompositeNode().SetForegroundOpacity(0.5)

    # Now link the views 
    sliceCompositeNodes = slicer.util.getNodesByClass("vtkMRMLSliceCompositeNode")
    for compositeNode in sliceCompositeNodes:
        compositeNode.SetLinkedControl(True)


button = qt.QPushButton("Next")
button.connect("clicked()", load)
button.show()

load()



####### The same labels in the gt and pred ####### 

# BASE_IMAGES = "D:\\deepa\\SynthSeg\\validation\\amos\\processed\\mr_images_train"
# BASE_LABELS =  "D:\\deepa\\SynthSeg\\testing\\amos\\mr_train\\gt_with_only_overlapping_labels"
# BASE_RESULTS = "D:\\deepa\\SynthSeg\\testing\\amos\\mr_train\\pred_resampled_with_only_overlapping_labels"
#
# resultIndex = 0
# labelNode = None
# resultNode = None
# volumeNode = None
# resultPaths = glob.glob(f"{BASE_RESULTS}/*.nii.gz")
#
# print('BASE_RESULTS: ' + str(BASE_RESULTS))
# print('resultPaths: ' + str(resultPaths))
#
# def load():
#
#     global resultIndex, labelNode, volumeNode, resultNode, resultPaths
#     for node in [labelNode, volumeNode, resultNode]:
#         if node:
#             slicer.mrmlScene.RemoveNode(node)
#     resultPath = resultPaths[resultIndex]
#     print('resultPath: ' + str(resultPath))
#     resultIndex += 1
#     resultNode = slicer.util.loadSegmentation(resultPath)
#
#     patientID = resultPath.split("\\")[-1]
#     print('patientID: ' + str(patientID))
#
#     labelFileName = os.path.join(BASE_LABELS,patientID)
#     print('labelFileName: ' + str(labelFileName))
#     labelNode = slicer.util.loadSegmentation(labelFileName)
#
#     volumeFileName = os.path.join(BASE_IMAGES, patientID)
#     print('volumeFileName: ' + str(volumeFileName))
#     volumeNode = slicer.util.loadVolume(volumeFileName, properties={"singleFile": True})
#
#     #slicer.modules.volumes.logic().ApplyVolumeDisplayPreset(volumeNode.GetVolumeDisplayNode(), "CT_ABDOMEN")
#     resultNode.GetDisplayNode().SetAllSegmentsOpacity2DFill(1.0)
#     resultNode.GetDisplayNode().SetAllSegmentsOpacity2DOutline(0.0)
#     labelNode.GetDisplayNode().SetAllSegmentsOpacity2DFill(0.0)
#     labelNode.GetDisplayNode().SetAllSegmentsOpacity2DOutline(1.0)
#     labelNode.GetDisplayNode().SetSliceIntersectionThickness(3)
#
# button = qt.QPushButton("Next")
# button.connect("clicked()", load)
# button.show()
#
# load()