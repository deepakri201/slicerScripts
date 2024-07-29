# /Applications/Slicer\ 4.app/Contents/MacOS/Slicer --python-script /Users/dk422/git/slicerScripts/abdomen_exp4/slicer_algorithm_comparison_scene.py

import slicer

def loadPatientData(mrbFilePath, volumeNodeNames, segmentationNodeNames, labelMapNodeNames):
    # Load the saved MRB file to set up the scene
    slicer.mrmlScene.Clear(0)
    slicer.util.loadScene(mrbFilePath)
    
    # Load new patient data
    newVolumeNodes = [slicer.util.loadVolume(name) for name in volumeNodeNames]
    newSegmentationNodes = [slicer.util.loadSegmentation(name) for name in segmentationNodeNames]
    newLabelMapNodes = [slicer.util.loadLabelVolume(name) for name in labelMapNodeNames]
    
    # Set the new nodes in the scene
    # This example assumes you have 4 views (adjust as needed)
    viewNames = ['Red', 'Yellow', 'Green', 'Slice4']
    layoutManager = slicer.app.layoutManager()
    
    for i, viewName in enumerate(viewNames):
        sliceWidget = layoutManager.sliceWidget(viewName)
        sliceLogic = sliceWidget.sliceLogic()
        sliceCompositeNode = sliceLogic.GetSliceCompositeNode()
        
        # Set the new volume node
        sliceCompositeNode.SetBackgroundVolumeID(newVolumeNodes[i].GetID())
        
        # Set the new segmentation node (if applicable)
        segmentationDisplayNode = newSegmentationNodes[i].GetDisplayNode()
        if segmentationDisplayNode:
            sliceViewNode = slicer.mrmlScene.GetNodeByID(viewName + 'View')
            segmentationDisplayNode.AddViewNodeID(sliceViewNode.GetID())
        
        # Set the new label map node (if applicable)
        labelMapDisplayNode = newLabelMapNodes[i].GetDisplayNode()
        if labelMapDisplayNode:
            sliceCompositeNode.SetForegroundVolumeID(newLabelMapNodes[i].GetID())
            sliceCompositeNode.SetForegroundOpacity(0.5)  # Adjust as needed

# Example usage
mrbFilePath = "/Users/dk422/Documents/SynthSeg/algorithm_comparison/amos_0507/scene.mrb"
volumeNodeNames = ["/Users/dk422/Documents/SynthSeg/validation/amos/processed/mr_images_train/amos_0508.nii.gz", 
                  "/Users/dk422/Documents/SynthSeg/validation/amos/processed/mr_images_train/amos_0508.nii.gz", 
                  "/Users/dk422/Documents/SynthSeg/validation/amos/processed/mr_images_train/amos_0508.nii.gz",
                  "/Users/dk422/Documents/SynthSeg/validation/amos/processed/mr_images_train/amos_0508.nii.gz",]
segmentationNodeNames = ["/Users/dk422/Documents/SynthSeg/abdomen_exp4B/synthetic_results/amos22_mr_train/prediction_results_resampled/dice_100/amos_0508_synthseg.nii.gz", 
                        "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/totalsegmri_results/amos22_mr_train/prediction_results_formatted/amos_0508.nii.gz", 
                        "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/mrsegmentator_results/amos22_mr_train/prediction_results_formatted/amos_0508_seg.nii.gz", 
                        "/Users/dk422/Documents/SynthSeg/abdomen_exp4B/mrisegmentatorabdomen_results/amos22_mr_train/prediction_results_formatted/amos_0508.nii.gz"]
labelMapNodeNames = ["/Users/dk422/Documents/SynthSeg/validation/amos/processed/mr_labels_train/amos_0508.nii.gz", 
                    "/Users/dk422/Documents/SynthSeg/validation/amos/processed/mr_labels_train/amos_0508.nii.gz", 
                    "/Users/dk422/Documents/SynthSeg/validation/amos/processed/mr_labels_train/amos_0508.nii.gz", 
                    "/Users/dk422/Documents/SynthSeg/validation/amos/processed/mr_labels_train/amos_0508.nii.gz"]

loadPatientData(mrbFilePath, volumeNodeNames, segmentationNodeNames, labelMapNodeNames)


