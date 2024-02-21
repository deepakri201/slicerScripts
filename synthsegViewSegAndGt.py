# Modified from Steve Pieper's script: https://github.com/pieper/nnmouse/blob/main/mouse-review.py
# 
# To run: 
# cd to C:\Users\deepa\AppData\Local\slicer.org\Slicer 5.6.1
# Slicer.exe --python-script "D://deepa//Slicer//SynthSegViewSegAndGt//synthsegViewSegAndGt.py" # --no-splash  --no-main-window

# Slicer.exe --python-script "C://Users//deepa//git//slicerScripts//synthsegViewSegAndGt.py"
# 
# First iteration - display gt and pred when both have same labels 
# Second iteration - display gt and pred when both have different labels, match color according to id 
# Third iteration - modify the names according to TotalSegmentator names 
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
color_table_filename = 'D:/deepa/Slicer/SynthSegViewSegAndGt/color_table_Slicer.ctbl'

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

###### Gt and pred have different labels, color the labels according to the same id #####

### MR AMOS TRAIN 
# BASE_IMAGES = "D:\\deepa\\SynthSeg\\validation\\amos\\processed\\mr_images_train"
# BASE_LABELS = "D:\\deepa\\SynthSeg\\validation\\amos\\processed\\mr_labels_train"
# BASE_RESULTS = "D:\\deepa\\SynthSeg\\testing\\amos\\mr_train\\pred_resampled"
# use_original_name_labels = 1 
# use_original_name_results = 1 
# labels_exist = 1 

### MR AMOS VAL 
# BASE_IMAGES = "D:\\deepa\\SynthSeg\\validation\\amos\\processed\\mr_images_val"
# BASE_LABELS = "D:\\deepa\\SynthSeg\\validation\\amos\\processed\\mr_labels_val"
# BASE_RESULTS = "D:\\deepa\\SynthSeg\\testing\\amos\\mr_val\\pred_resampled"
# use_original_name_labels = 1
# use_original_name_results = 1 
# labels_exist = 1 

### T2 Kidney healthy 
# BASE_IMAGES = "D:\\deepa\\SynthSeg\\validation\\T2WeightedKidneyMRISegmentation\\processed\\Healthy_Control\\images"
# BASE_LABELS = "D:\\deepa\\SynthSeg\\validation\\T2WeightedKidneyMRISegmentation\\processed\\Healthy_Control\\labels"
# BASE_RESULTS = "D:\\deepa\\SynthSeg\\testing\\T2WeightedKidneyMRISegmentation\\Healthy_Control\\pred_resampled"
# use_original_name_labels = 0 
# use_original_name_results = 1 
# labels_exist = 1 

### T2 Kidney CKD 
# BASE_IMAGES = "D:\\deepa\\SynthSeg\\validation\\T2WeightedKidneyMRISegmentation\\processed\\CKD\\images"
# BASE_LABELS = "D:\\deepa\\SynthSeg\\validation\\T2WeightedKidneyMRISegmentation\\processed\\CKD\\labels"
# BASE_RESULTS = "D:\\deepa\\SynthSeg\\testing\\T2WeightedKidneyMRISegmentation\\CKD\\pred_resampled"
# use_original_name_labels = 0 
# use_original_name_results = 1 
# labels_exist = 1 

# ### TCGA-LIHC AIMI BANF ### 
# BASE_IMAGES = "D:\\deepa\\SynthSeg\\testing\\tcga_lihc_aimi_banf\\nii_3d"
# BASE_RESULTS = "D:\\deepa\\SynthSeg\\testing\\tcga_lihc_aimi_banf\\pred_3d"
# use_original_name_labels = 1 
# use_original_name_results = 0 
# labels_exist = 0 


### CHAOS validation ### 
BASE_IMAGES = "D:\\deepa\\SynthSeg\\validation\\CHAOS\\images_with_synthseg_ext"
# BASE_LABELS = "D:\\deepa\\SynthSeg\\validation\\CHAOS\\labels"
BASE_LABELS = "D:\\deepa\\SynthSeg\\validation\\CHAOS\\pred_resampled\\dice_001"
BASE_RESULTS = "D:\\deepa\\SynthSeg\\validation\\CHAOS\\pred_resampled\\dice_100"
use_original_name_labels = 1
use_original_name_results = 1 
labels_exist = 1 

resultIndex = 0
labelNode = None
resultNode = None
volumeNode = None
resultPaths = glob.glob(f"{BASE_RESULTS}/*.nii.gz")

print('BASE_RESULTS: ' + str(BASE_RESULTS))
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
      labelNode = slicer.util.loadSegmentation(labelFileName, {'colorNodeID': colorNode.GetID()})

    volumeFileName = os.path.join(BASE_IMAGES, patientID)
    print('volumeFileName: ' + str(volumeFileName))
    volumeNode = slicer.util.loadVolume(volumeFileName, properties={"singleFile": True})

    #slicer.modules.volumes.logic().ApplyVolumeDisplayPreset(volumeNode.GetVolumeDisplayNode(), "CT_ABDOMEN")
    resultNode.GetDisplayNode().SetAllSegmentsOpacity2DFill(1.0)
    resultNode.GetDisplayNode().SetAllSegmentsOpacity2DOutline(0.0)
    
    if (labels_exist):
      labelNode.GetDisplayNode().SetAllSegmentsOpacity2DFill(0.0)
      labelNode.GetDisplayNode().SetAllSegmentsOpacity2DOutline(1.0)
      labelNode.GetDisplayNode().SetSliceIntersectionThickness(3)

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
