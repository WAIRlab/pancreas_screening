# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 10:02:09 2021

@author: X1 Carbon

from control and PDAC original file, recursive preprocess the image, 
save images to the new filepath, create json file

save created pandas file
"""

import os
import pandas as pd
import shutil
import json
import SimpleITK as sitk
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)
rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
log_path = os.getcwd() + '/Logs/'
log_name = log_path + rq + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

# Data_path = 'E:\\origin_file'
Data_path = 'E:\\test_extra'
# Data_path = 'C:\\Users\\X1 Carbon\\Documents\\RawData\\pancreatic_seg'

'''
从数据路径中加载DICOM数据，根据dicom数据解析头文件
'''
def traversal_dcm(file_path):
    Header_info = []
    for root, dirs, files in os.walk(file_path):
        for name in files:
            dicom_path = os.path.join(root, name)
            try:
                name = os.path.dirname(dicom_path)
                img = sitk.ReadImage(dicom_path)
                ImageUID = str(img.GetMetaData('0008|0018')) if img.HasMetaDataKey('0008|0018') else 0.0
                studyUID = str(img.GetMetaData('0020|000D')) if img.HasMetaDataKey('0020|000D') else 0.0
                seriesUID = str(img.GetMetaData('0020|000e')) if img.HasMetaDataKey('0020|000e') else 0.0
                series_desc = str(img.GetMetaData('0008|103e')) if img.HasMetaDataKey('0008|103e') else 0.0
                series_num = str(img.GetMetaData('0020|0011')) if img.HasMetaDataKey('0020|0011') else 0.0
                model_num = str(img.GetMetaData('0008|1090')) if img.HasMetaDataKey('0008|1090') else 0.0
                acquisition_num = str(img.GetMetaData('0020|0012')) if img.HasMetaDataKey('0020|0012') else 0.0
                manufacturer = str(img.GetMetaData('0008|0070')) if img.HasMetaDataKey('0008|0070') else 0.0
                ID = str(img.GetMetaData('0010|0020')) if img.HasMetaDataKey('0010|0020') else 0.0
                sex = str(img.GetMetaData('0010|0040')) if img.HasMetaDataKey('0010|0040') else 0.0
                study_date = str(img.GetMetaData('0008|0020')) if img.HasMetaDataKey('0008|0020') else 0.0
                # aq_date = str(img.GetMetaData(0, '0008|0022'))
                header_info = [dicom_path, ImageUID, studyUID, seriesUID, series_desc, series_num,
                               model_num, acquisition_num, manufacturer,ID, sex, study_date]
                Header_info.append(header_info)
                # print(header_info)
            except Exception as e:
                print('error file', dicom_path)
                pass
    
    Header_info_df = pd.DataFrame(Header_info, 
                                  columns= ['name', 'ImageUID', 'studyUID', 'seriesUID', 'series_desc', 
                                            'series_num', 'model_num', 'acquisition_num', 'manufacturer', 
                                            'ID', 'sex', 'study_date'] )
    # Header_info_df['model_num'] = Header_info_df['model_num'].apply(lambda x:x.strip())
    # Header_info_df['manufacturer'] = Header_info_df['manufacturer'].apply(lambda x:x.strip())
    Header_info_df = Header_info_df.drop(index = Header_info_df.series_desc[Header_info_df.series_desc ==0].index)
    return(Header_info_df)


study_list = os.listdir(Data_path)
# for study in study_list:
study='normal' 
try:
    study_path = os.path.join(Data_path, study)
    Header_info_df = traversal_dcm(study_path)
    Header_info_df['studyUID']=Header_info_df['name'].map(lambda x: os.path.dirname((os.path.dirname(x))) )
    Header_info_df['seriesFolder']=Header_info_df['name'].map(lambda x:x.split('\\')[-2])
    Header_info_df = Header_info_df.applymap(lambda row: str(row))
    Header_info_df = Header_info_df.applymap(lambda row:row.strip())
# Header_info_df['acquisition_num']=Header_info_df['acquisition_num'].apply(lambda x:x.strip())
# Header_info_df.to_csv('img_header.csv')

    '''
    logger.info('finish creating json start processing')
    os.system('rm -rf /data/VPS/VPS_03/lmq/PAII/panc_seg_deploy_weining/panc_seg_deploy_v0/results/converted_nii')
    os.system('sh /data/VPS/VPS_03/lmq/PAII/panc_seg_deploy_weining/panc_seg_deploy_v0/app/run_docker.sh')
    os.system('rm -rf /data/VPS/VPS_03/lmq/PAII/panc_seg_deploy_weining/panc_seg_deploy_v0/data/*')
    if os.path.exists(os.path.join(output_path,study+'_final_seg.nii.gz')) == True:
        shutil.move(os.path.join(Data_path, study), os.path.join(processed_path, study))
        logger.info('finish processing study ', study)
    '''
except:
    logger.debug('error at study', study)
    pass

Header_info_df.to_csv('data\\pancreas_dcm_test_normal_updated.csv')