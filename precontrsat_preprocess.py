# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 14:08:28 2022

@author: liumingqian
"""


import SimpleITK as sitk
import os
import pandas as pd
import logging

# Data_path = 'E:\\origin_file'
Data_path='E:\\train_extra'
output_path = 'E:\\precontrast_image_updated'
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
                ImageUID = str(img.GetMetaData('0010|0020')) if img.HasMetaDataKey('0010|0020') else 0.0
                studyUID = str(img.GetMetaData('0020|000D')) if img.HasMetaDataKey('0020|000D') else 0.0
                seriesUID = str(img.GetMetaData('0020|000e')) if img.HasMetaDataKey('0020|000e') else 0.0
                series_desc = str(img.GetMetaData('0008|103e')) if img.HasMetaDataKey('0008|103e') else 0.0
                series_num = str(img.GetMetaData('0020|0011')) if img.HasMetaDataKey('0020|0011') else 0.0
                model_num = str(img.GetMetaData('0008|1090')) if img.HasMetaDataKey('0008|1090') else 0.0
                acquisition_num = str(img.GetMetaData('0020|0012')) if img.HasMetaDataKey('0020|0012') else 0.0
                # study_desc = str(img.GetMetaData('0008|1030')) if img.HasMetaDataKey('0008|1030') else 0.0
                manufacturer = str(img.GetMetaData('0008|0070')) if img.HasMetaDataKey('0008|0070') else 0.0
                # aq_date = str(img.GetMetaData(0, '0008|0022'))
                header_info = [dicom_path, ImageUID, studyUID, seriesUID, series_desc, series_num,
                               model_num, acquisition_num, manufacturer]
                Header_info.append(header_info)
                # print(header_info)
            except Exception as e:
                print('error file', dicom_path)
                pass
    
    Header_info_df = pd.DataFrame(Header_info, 
                                  columns= ['name', 'ImageUID', 'studyUID', 'seriesUID', 'series_desc', 
                                            'series_num', 'model_num', 'acquisition_num', 'manufacturer'] )
    # Header_info_df['model_num'] = Header_info_df['model_num'].apply(lambda x:x.strip())
    # Header_info_df['manufacturer'] = Header_info_df['manufacturer'].apply(lambda x:x.strip())
    Header_info_df = Header_info_df.drop(index = Header_info_df.series_desc[Header_info_df.series_desc ==0].index)
    return(Header_info_df)

'''
胰腺平扫图像保存为 PDAC_SEG文件名_precontrast.nii.gz
'''
def copy_list_data(list_data):
    dcm_dir = os.path.dirname(list_data[0])
    print(dcm_dir)
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(dcm_dir)
    reader.SetFileNames(dicom_names)
    img = reader.Execute()
    return img

'''
找到3mm的胰腺平扫图像
'''
def calculate_prcontrast(Header_info_df,groupname, study_name):
    model_list = set(Header_info_df['model_num'].tolist())
    print(model_list)
    print(set(Header_info_df['series_desc'].tolist()))
    logging.info(model_list)
    for model_info in model_list:
        print(model_info)
    		# try:
        if 'iCT 256' in model_info:
            # print(Header_info_df.groupby('seriesUID'))
            series_group = Header_info_df.groupby('seriesUID')
            series_info = list(series_group)
            for series in series_info:
                series_desc = series[1]['series_desc'].tolist()[0]
                series_num = series[1]['series_num'].tolist()[0]
                print(series_num)
                if '1mm Pancreas, iDose' in series_desc:
                    img = copy_list_data(series[1]['name'].tolist())
                    print(study_name)
                    output_file = os.path.join(output_path,groupname,'PDAC_SEG'+study_name + "_0000.nii.gz")
                    sitk.WriteImage(img, output_file)
                elif series_num == 201:
                    img = copy_list_data(series[1]['name'].tolist())
                    print(study_name)
                    output_file = os.path.join(output_path,groupname,'PDAC_SEG'+study_name + "_0000.nii.gz")
                    sitk.WriteImage(img, output_file)
                elif '1mm ABD, iDose' in series_desc:
                    img = copy_list_data(series[1]['name'].tolist())
                    print(study_name)
                    output_file = os.path.join(output_path,groupname,'PDAC_SEG'+study_name + "_0000.nii.gz")
                    sitk.WriteImage(img, output_file)
        elif 'Aquilion ONE' in model_info:
            series_group = Header_info_df.groupby('seriesUID')
            series_info = list(series_group)
            for series in series_info:
                series_desc = series[1]['series_desc'].tolist()[0]
                if (series_desc =='Body 1.0') or (series_desc =='CTA 1.0') or (series_desc =='CTA 5.0'):
                    img = copy_list_data(series[1]['name'].tolist())
                    print(study_name)
                    output_file = os.path.join(output_path,groupname,'PDAC_SEG'+study_name + "_0000.nii.gz")
                    sitk.WriteImage(img, output_file)
    		
        elif 'Brilliance 16P' in model_info:
            series_group = Header_info_df.groupby('seriesUID')
            series_info = list(series_group)
            for series in series_info:
                series_num = series[1]['series_num'].tolist()[0]
                if '2' in series_num:
                    img = copy_list_data(series[1]['name'].tolist()) 
                    print(study_name)
                    output_file = os.path.join(output_path,groupname,'PDAC_SEG'+study_name + "_0000.nii.gz")
                    sitk.WriteImage(img, output_file)
    		
        elif 'Sensation Cardiac 64' in model_info:
            series_group = Header_info_df.groupby('seriesUID')
            series_info = list(series_group)
            for series in series_info:
                series_desc = series[1]['series_desc'].tolist()[0]
                if 'C-  1.0  B30f ' in series_desc: 
                    img = copy_list_data(series[1]['name'].tolist())
                    print(study_name)
                    output_file = os.path.join(output_path,groupname, 'PDAC_SEG'+study_name + "_0000.nii.gz")
                    sitk.WriteImage(img, output_file)
		
	# except:
    #     logging.info("error")
    #     pass
    return
'''
study_list = os.listdir(Data_path)
for study in study_list:
    print(study)
    study_path = os.path.join(Data_path, study)
    Header_info_df = traversal_dcm(study_path)
    print(Header_info_df)
    calculate_prcontrast(Header_info_df)
'''

def name_patientID_info(filepath):
    img = sitk.ReadImage(filepath)
    patientsname = str(img.GetMetaData('0010|0010')) if img.HasMetaDataKey('0010|0010') else 0.0
    ID = str(img.GetMetaData('0010|0020')) if img.HasMetaDataKey('0010|0020') else 0.0
    sex = str(img.GetMetaData('0010|0040')) if img.HasMetaDataKey('0010|0040') else 0.0
    study_date = str(img.GetMetaData('0008|0020')) if img.HasMetaDataKey('0008|0020') else 0.0
    return [patientsname, ID, sex, study_date]


Header_info_df = pd.read_csv('data\\pancreas_dcm_test_updated.csv')
Header_info_df = Header_info_df.dropna()
group = Header_info_df.groupby('studyUID')
image_info = list(group)
for study_details in image_info:
    try:
        sample_name = study_details[1][:1]['name'].tolist()[0]
        groupname = 'PDAC_test'
        # groupname = sample_name.split('\\')[2]
        patient_info = name_patientID_info(sample_name)
        print(patient_info[1]+'_'+patient_info[3])
        calculate_prcontrast(study_details[1], groupname, patient_info[1]+'_'+patient_info[3])

    except:
        print('error at study', study_details[0])
        pass

