# Modified from Steve Pieper's script: https://github.com/pieper/nnmouse/blob/main/mouse-review.py
# 
# To run: 
# cd to C:\Users\deepa\AppData\Local\slicer.org\Slicer 5.6.1
# Slicer.exe --python-script "D://deepa//Slicer//SynthSegViewSegAndGt//synthsegViewSegSequence.py" # --no-splash  --no-main-window
# Slicer.exe --python-script "C://Users//deepa//git//slicerScripts//synthsegViewSegSequence.py"
# 
# Click to load next patient. 
# Use sequenceBrowser to play through the SEG for each validation epoch. 
# 
# Deepa Krishnaswamy 
# Brigham and Women's Hospital 
# January 2024 
##########################################################################################################

##################
### Parameters ### 
##################

form_color_table = 0 
# color_table_filename = 'D:/deepa/Slicer/SynthSegViewSegAndGt/color_table_totalSegmentator.ctbl'

# https://sashamaps.net/docs/resources/20-colors/ 
# color_table_filename = 'D:/deepa/Slicer/SynthSegViewSegAndGt/color_table_Slicer.ctbl'
color_table_filename = 'C:/Users/deepa/git/slicerScripts/color_table_Slicer.ctbl'

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
    
try:
  import totalsegmentator 
except ModuleNotFoundError:
  if slicer.util.confirmOkCancelDisplay("This module requires 'totalsegmentator' Python package. Click OK to install it now."):
    slicer.util.pip_install("totalsegmentator")
    import totalsegmentator

##################
### Set up ### 
##################

### AMOS validation MR ###
BASE_IMAGES = "D:\\deepa\\SynthSeg\\validation\\amos\\processed\\mr_images_train_synthseg_ext"
BASE_RESULTS = "D:\\deepa\\SynthSeg\\validation\\amos\\processed\\mr_pred_train_exp2"
# BASE_LABELS = "D:\\deepa\\SynthSeg\\validation\\amos\\processed\\mr_pred_train_exp2"
BASE_LABELS = "D:\\deepa\\SynthSeg\\validation\\amos\\processed\\mr_labels_train_synthseg_ext"
use_original_name_labels = 1 
use_original_name_results = 1 
labels_exist = 1

### AMOS validation CT### 
BASE_IMAGES = "D:\\deepa\\SynthSeg\\validation\\amos\\processed\\ct_images_train_synthseg_ext"
BASE_RESULTS = "D:\\deepa\\SynthSeg\\validation\\amos\\processed\\ct_pred_train_exp2"
# BASE_LABELS = "D:\\deepa\\SynthSeg\\validation\\amos\\processed\\ct_pred_train_exp2"
BASE_LABELS = "D:\\deepa\\SynthSeg\\validation\\amos\\processed\\ct_labels_train_synthseg_ext"
use_original_name_labels = 1 
use_original_name_results = 1 
labels_exist = 1

##################
### Initialize ### 
##################

resultIndex = 0
labelNode = None
resultNode = None
volumeNode = None
# resultPaths = glob.glob(f"{BASE_RESULTS}/*.nii.gz")
# list of subdirectories 
subDirs = glob.glob(f"{BASE_RESULTS}/*/") 
# Now get list of patientids from first 
subDir0 = subDirs[0] 
resultPaths = glob.glob(f"{subDir0}/*.nii.gz") 

print('BASE_RESULTS: ' + str(BASE_RESULTS))
print('subDirs: ' + str(subDirs))
print('resultPaths: ' + str(resultPaths))

########################
### form color table ### 
########################
if (form_color_table):
    
  # Create a list of colors, of length of label list: 
  # Labels from TotalSegmentator
  labels_ts = [1,2,3,4,5,6,10,11,12,18,55,56,57,90,91,92,
               94,95,96,97,98,99,100,101,102,103]
  
  # Get the names and label ids from the TotalSegmentator map to binary
  from totalsegmentator.map_to_binary import class_map
  # url = 'https://raw.githubusercontent.com/wasserth/TotalSegmentator/master/totalsegmentator/map_to_binary.py'
  # download = requests.get(url).content
  # # Reading the downloaded content and turning it into a pandas dataframe
  # # class_map = pd.read_csv(io.StringIO(download.decode('utf-8')))
  # class_map = pd.read_csv(io.StringIO(str(download,'utf-8')))
  # print (class_map.head())
  total_v1 = class_map['total_v1']
  total_label_names = list(total_v1.keys())
  labels_names = [total_v1[key] for key in labels_ts]
  
  labels_ts_df = pd.DataFrame()
  labels_ts_df['label_id'] = labels_ts 
  labels_ts_df['label_name'] = labels_names
  
  # Get the colors from the new TotalSegmentator file 
  snomed_mapping_ts_file = "D:/deepa/Slicer/SynthSegViewSegAndGt/totalsegmentator_snomed_mapping_with_partial_colors.csv" 
  snomed_mapping_ts_df = pd.read_csv(snomed_mapping_ts_file)
  
  # Join the names on the map to binary colors to get list of colors 
  # labels_ts_df_merged = pd.join([labels_ts_df, snomed_mapping_ts_df], )
  labels_ts_df_merged = pd.merge(labels_ts_df, snomed_mapping_ts_df, how='left', left_on=['label_name'], right_on=['Structure'])
  labels_ts_df_merged = labels_ts_df_merged[['label_id', 'label_name', 'recommendedDisplayRGBValue']]

  # Form the color table file from the dataframe 
  color_table_df = pd.DataFrame()
  color_table_df['label_id'] = labels_ts_df_merged['label_id']
  color_table_df['label_name'] = labels_ts_df_merged['label_name']
  rgb = labels_ts_df_merged['recommendedDisplayRGBValue'].values 
  r_list = []; b_list = []; g_list = []; last_col_list = [] 
  
  for n in range(0,len(rgb)): 
    val = rgb[n]
    val =  val[1:-2] # remove brackets
    val_array = val.split(',')
    r_list.append(int(val_array[0])) 
    g_list.append(int(val_array[1]))
    b_list.append(int(val_array[2]))
    last_col_list.append(255)
  
  color_table_df['R'] = r_list 
  color_table_df['G'] = g_list 
  color_table_df['B'] = b_list
  color_table_df['last_col'] = last_col_list
  
  # Insert background as first row 
  color_table_df.loc[-1] = [0, 'Background', 0, 0, 0, 0] # adding row
  color_table_df.index = color_table_df.index + 1 # shifting index 
  color_table_df.sort_index(inplace=True)
  
  # Save color table 
  color_table_df.to_csv(color_table_filename, header=None, index=None, sep=' ', mode='w')
  
  # segmentation = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLSegmentationNode').GetSegmentation()
  # segmentation.GetNthSegment(0).SetColor(1,0,0)



def load():
  
    ###################################
    ### Delete nodes from the scene ###
    ###################################
    
    # Delete all segmentation nodes in scene
    existingSegNodes = slicer.util.getNodesByClass("vtkMRMLSegmentationNode")
    for node in existingSegNodes:
      slicer.mrmlScene.RemoveNode(node)
    # Delete volume nodes from scene 
    existingVolumeNodes = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
    for node in existingVolumeNodes:
      slicer.mrmlScene.RemoveNode(node)
    # Delete sequences node from scene 
    existingSeqNodes = slicer.util.getNodesByClass("vtkMRMLSequenceNode")
    for node in existingSeqNodes:
      slicer.mrmlScene.RemoveNode(node)
    

    #################
    ### Set nodes ###
    #################
    
    colorNode = slicer.util.loadColorTable(color_table_filename)

    global resultIndex, labelNode, volumeNode, resultNode, resultPaths
    for node in [labelNode, volumeNode, resultNode]:
        if node:
            slicer.mrmlScene.RemoveNode(node)
    resultPath = resultPaths[resultIndex]
    print('resultPath: ' + str(resultPath))
    resultIndex += 1
    resultNode = slicer.util.loadSegmentation(resultPath, {'colorNodeID': colorNode.GetID()})

    if (use_original_name_results): 
      patientID = resultPath.split("\\")[-1]
    else: 
      patientID = resultPath.split("\\")[-1].split('_')[0] + '_' + resultPath.split("\\")[-1].split('_')[1] + '.nii.gz'
    print('patientID: ' + str(patientID))
    
    if (labels_exist): 
      if (use_original_name_labels):
          labelFileName = os.path.join(BASE_LABELS,patientID)
      else: 
          labelFileName = os.path.join(BASE_LABELS,patientID.split('.')[0] + '_mask.nii.gz')
      print('labelFileName: ' + str(labelFileName))
      print(os.path.exists(labelFileName))
    # labelNode = slicer.util.loadSegmentation(labelFileName, {'colorNodeID': colorNode.GetID()})

    volumeFileName = os.path.join(BASE_IMAGES, patientID)
    print('volumeFileName: ' + str(volumeFileName))
    volumeNode = slicer.util.loadVolume(volumeFileName, properties={"singleFile": True})
    # Turn the image volume on
    # volumeNode.SetDisplayVisibility(1)

    # resultNode.GetDisplayNode().SetAllSegmentsOpacity2DFill(1.0)
    # resultNode.GetDisplayNode().SetAllSegmentsOpacity2DOutline(0.0)
    # if (labels_exist):
    #   labelNode.GetDisplayNode().SetAllSegmentsOpacity2DFill(0.0)
    #   labelNode.GetDisplayNode().SetAllSegmentsOpacity2DOutline(1.0)
    #   labelNode.GetDisplayNode().SetSliceIntersectionThickness(3)
      
      
    ### Sequence node ### 
    sequence_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode")
    nifti_files = [os.path.join(f, patientID) for f in subDirs]
    # print('nifti_files: ' + str(nifti_files))
          
    for index, nifti_file in enumerate(nifti_files):
      # file_path = os.path.join(directory_path, nifti_file)
      file_path = nifti_file
      # Load the volume into 3D Slicer
      # volume_node = slicer.util.loadVolume(file_path)
      volume_node = slicer.util.loadSegmentation(file_path, {'colorNodeID': colorNode.GetID()})
      # Add the volume to the sequenceNode
      sequence_node.SetDataNodeAtValue(volume_node, str(index))
    # Set the sequenceNode as the active sequence in the layout
    # slicer.app.layoutManager().sequenceBrowser().setMasterSequenceNode(sequence_node)
    
    # https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html 
    # Create a sequence browser node for the new merged sequence
    mergedSequenceBrowserNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceBrowserNode", "Merged")
    mergedSequenceBrowserNode.AddSynchronizedSequenceNode(sequence_node)
    slicer.modules.sequences.toolBar().setActiveBrowserNode(mergedSequenceBrowserNode)
    # Show proxy node in slice viewers
    mergedProxyNode = mergedSequenceBrowserNode.GetProxyNode(sequence_node)
    # slicer.util.setSliceViewerLayers(background=mergedProxyNode)
    
    # Set frame rate
    # mergedSequenceBrowserNode.SetAttribute('FrameRate', str(1.0))
    # sequence_node.SetAttribute('FrameRate', str(1.0))
    # mergedProxyNode.SetAttribute('FrameRate', str(1.0))

    # Set volume node 
    slicer.mrmlScene.AddNode(volumeNode)
    displayNode=slicer.vtkMRMLScalarVolumeDisplayNode()
    slicer.mrmlScene.AddNode(displayNode)
    
    # Switch to sequence browser 
    # slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout_SequenceBrowserView)
    slicer.util.selectModule("Sequences")
    # slicer.modules.sequences.showSequenceBrowser(mergedSequenceBrowserNode)
    
    # Delete all segmentation nodes in scene
    existingSegNodes = slicer.util.getNodesByClass("vtkMRMLSegmentationNode")
    for node in existingSegNodes:
      slicer.mrmlScene.RemoveNode(node)
      
    # add in labelNode for outline (ground truth)
    labelNode = slicer.util.loadSegmentation(labelFileName, {'colorNodeID': colorNode.GetID()})
    if (labels_exist):
      labelNode.GetDisplayNode().SetAllSegmentsOpacity2DFill(0.0)
      labelNode.GetDisplayNode().SetAllSegmentsOpacity2DOutline(1.0)
      labelNode.GetDisplayNode().SetSliceIntersectionThickness(3)

    # Set frame rate to 1 frame per second 
    # sequence_node.SetIndexingRate(1.0)
    
    # Play sequence
    # slicer.app.layoutManager().sequenceBrowser().playSequence()



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
