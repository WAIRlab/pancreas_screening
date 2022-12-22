# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 10:23:37 2022

@author: liumingqian

一个文档下有多个seriesuid,只传输一个
根据生成的dafaframe文件，根据每个studyuid作为一个study来判断下面的series是否符合要求,
对于每个study提取第一张图象患者姓名、年龄、影像号作为基本信息，将影像号作为study的文件名进行保存

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
new_path = 'E:\\prepared_dcm_file_updated'
# output_path = '/data/VPS/VPS_03/lmq/PAII/panc_seg_deploy_weining/panc_seg_deploy_v0/results/segmentation'
# processed_path = '/data/VPS/VPS_03/lmq/PAII/panc_seg_deploy_weining/panc_seg_deploy_v0/results/segmentation/data_processed'

'''
根据已知的series名字，构建新路径，将列表中的数据复制至目标文件夹
重新构建data目录， new_path+阳性or阴性+影像号+seriesUID
'''

def copy_list_data(list_data, patientID):
    for each_data in list_data:
        data_element = each_data.split('\\')
        dest_path = os.path.join(new_path, data_element[2], patientID, data_element[-2], data_element[-1])
        if not os.path.exists(os.path.dirname(dest_path)):
            os.makedirs(os.path.dirname(dest_path))
        shutil.copyfile(each_data, dest_path)        
    return 

'''
遍历表格
根据manufacturer model 识别CT机器
根据识别的机器类别选择正确的series
根据series的组合，识别series的文件夹，复制文件到 胰腺分割目录下
将phase.json文件放到胰腺分割目录下
'''

def calculate_CE_rank(Header_acquilion_df):
    Header_aquilion = Header_acquilion_df[['series_desc','series_num','acquisition_num']]
    Header_aquilion = Header_aquilion.drop_duplicates()
    Header_aquilion = Header_aquilion[(Header_aquilion['series_desc']=='Body 1.0 CE')|(Header_aquilion['series_desc']=='CTA 2.0 CE')]
    Header_aquilion['rank'] = Header_aquilion['acquisition_num'].rank(ascending=0)
    acq_dict = Header_aquilion.set_index("acquisition_num")['rank'].to_dict()
    return acq_dict


def create_json(study, groupname, study_name):
    #  study_file = study[1]['name'][0]
    #   study_path = os.path.dirname(os.path.dirname(study_file))
    phase_info = {"venous":None, "arterial_late": None, "non-contrast": None,
                  "arterial_early":None, "delay":None}
    model_list = list(map(str.strip, study[1]['model_num'].tolist()))
    model_info = set(model_list)
    # logger.info(model_info)
    # try:
    if 'iCT 256' in model_info:
        series_group = study[1].groupby('seriesUID')
        series_info = list(series_group)
        for series in series_info:
            series_desc = str(series[1]['series_desc'].tolist()[0])
            series_folder = str(series[1]['seriesFolder'].tolist()[0])
            print(series_desc)
            # logger.info(format(str(series_desc), series[0], series_folder))
            if ('1mm ABD' in series_desc) or ('1mm Lung' in series_desc):
                phase_info['non-contrast']= series_folder
                copy_list_data(series[1]['name'].tolist(), study_name)
            elif 'A 1mm' in series_desc:
                phase_info['arterial_early'] = series_folder
                copy_list_data(series[1]['name'].tolist(), study_name)
            elif 'P 1mm' in series_desc:
                phase_info['arterial_late'] = series_folder
                copy_list_data(series[1]['name'].tolist(), study_name)
            elif 'D 1mm' in series_desc:
                phase_info['delay'] = series_folder
                copy_list_data(series[1]['name'].tolist(), study_name)
            elif 'P 1mm' in series_desc:
                phase_info['venous'] = series_folder
                copy_list_data(series[1]['name'].tolist(), study_name)
        # logger.info(format(phase_info))
        with open(os.path.join(new_path,groupname, study_name, 'phase_info.json'), 'w') as json_file:
            print('writing to ', os.path.join(new_path,groupname, study_name, 'phase_info.json'))
            json.dump(phase_info, json_file, ensure_ascii=False)
    elif 'Aquilion ONE' in model_info:
        series_group = study[1].groupby('seriesUID')
        series_info = list(series_group)
        acq_dict = calculate_CE_rank(study[1])
        print(acq_dict)
        for series in series_info:
            acq_num = series[1]['acquisition_num'].tolist()[0]
            series_desc = str(series[1]['series_desc'].tolist()[0])
            series_folder = str(series[1]['seriesFolder'].tolist()[0])
            print(acq_num, series_desc, series_folder)
            if (series_desc =='Body 1.0') or (series_desc =='Lung 1.0'):
                phase_info['non-contrast']= series_folder
                print('non-contrast', series_folder)
                copy_list_data(series[1]['name'].tolist(), study_name)
            elif '3.0 CE' in series_desc:
                if acq_dict[acq_num]==3:
                    phase_info['arterial_late'] = series_folder
                    copy_list_data(series[1]['name'].tolist(), study_name)
                    print('arterial_late', series_folder)
                elif acq_dict[acq_num]==2: 
                    phase_info['venous'] = series_folder
                    copy_list_data(series[1]['name'].tolist(), study_name)
                    print('venous', series_folder)
                elif  acq_dict[acq_num]==1: 
                    phase_info['delay'] = series_folder
                    copy_list_data(series[1]['name'].tolist(), study_name)
                    print('delay', series_folder)
                elif  acq_dict[acq_num]==4: 
                    phase_info['arterial_early'] = series_folder
                    copy_list_data(series[1]['name'].tolist(), study_name)
                    print('arterial_early', series_folder)
        print(phase_info)
        with open(os.path.join(new_path,groupname, study_name,'phase_info.json'), 'w') as json_file:
            print('writing to ', os.path.join(new_path,groupname, study_name, 'phase_info.json'))
            json.dump(phase_info, json_file, ensure_ascii=False)
    elif 'Brilliance 16P' in model_info:
        series_group = study[1].groupby('seriesUID')
        series_info = list(series_group)
        for series in series_info:
            series_num = str(series[1]['series_num'].tolist()[0])
            series_folder = str(series[1]['seriesFolder'].tolist()[0])
            print(series_num, series[0], series_folder)
            if '2' in series_num:
                phase_info['non-contrast']= series_folder
                copy_list_data(series[1]['name'].tolist(), study_name)
            elif '6' in series_num:
                phase_info['arterial_early'] = series_folder
                copy_list_data(series[1]['name'].tolist(), study_name)
            elif '7' in series_num:
                phase_info['venous'] = series_folder
                copy_list_data(series[1]['name'].tolist(), study_name)
            elif '8' in series_num:
                phase_info['delay'] = series_folder
                copy_list_data(series[1]['name'].tolist(), study_name)
        # logger.info(format(phase_info))
        with open(os.path.join(new_path, groupname, study_name, 'phase_info.json'), 'w') as json_file:
            print('writing to ', os.path.join(new_path,groupname, study_name, 'phase_info.json'))
            json.dump(phase_info, json_file, ensure_ascii=False)
    elif 'Sensation Cardiac 64' in model_info:
        series_group = study[1].groupby('seriesUID')
        series_info = list(series_group)
        for series in series_info:
            series_desc = str(series[1]['series_desc'].tolist()[0])
            series_folder = str(series[1]['seriesFolder'].tolist()[0])
            print(series_desc, series[0], series_folder)
            if 'Non Contrast  1.0  B30f' in series_desc:
                phase_info['non-contrast']= series_folder
                copy_list_data(series[1]['name'].tolist(), study_name)
            elif 'Arterial Phase  1.0  B20f' in series_desc:
                phase_info['arterial_early'] = series_folder
                copy_list_data(series[1]['name'].tolist(), study_name)
            elif 'Venous Phase  1.0  B30f' in series_desc:
                phase_info['venous'] = series_folder
                copy_list_data(series[1]['name'].tolist(), study_name)
            elif 'C+3  1.5  B30f' in series_desc:
                phase_info['delay'] = series_folder
                copy_list_data(series[1]['name'].tolist(), study_name)
        # logger.info(format(phase_info))
        with open(os.path.join(new_path,groupname, study_name, 'phase_info.json'), 'w') as json_file:
            print('writing to ', os.path.join(new_path,groupname, study_name, 'phase_info.json'))
            json.dump(phase_info, json_file, ensure_ascii=False)
    # except:
    #     print('error processing '+ study[0])
    #     pass
    return
'''
异常判断 late arterial -> early arterial ->venous
少要有平扫、arterial、venous
在subprocess中调用相关类别

{"venous": "1.2.392.200036.9116.2.5.1.48.1224104463.1541999963.601986", 
 "arterial_late": "1.2.392.200036.9116.2.5.1.48.1224104463.1541999952.884312",
 "non-contrast": "1.2.392.200036.9116.2.5.1.48.1224104463.1541999807.953681",
 "arterial_early": "1.2.392.200036.9116.2.5.1.48.1224104463.1541999866.358993", 
 "delay": "1.2.392.200036.9116.2.5.1.48.1224104463.1541999984.728717"}
执行 胰腺分割任务
读取返回的json文件
结果写回数据表中
'''

def name_patientID_info(filepath):
    img = sitk.ReadImage(filepath)
    patientsname = str(img.GetMetaData('0010|0010')) if img.HasMetaDataKey('0010|0010') else 0.0
    ID = str(img.GetMetaData('0010|0020')) if img.HasMetaDataKey('0010|0020') else 0.0
    sex = str(img.GetMetaData('0010|0040')) if img.HasMetaDataKey('0010|0040') else 0.0
    study_date = str(img.GetMetaData('0008|0020')) if img.HasMetaDataKey('0008|0020') else 0.0
    return [patientsname, ID, sex, study_date]

Header_info_df = pd.read_csv('data\\pancreas_dcm_test_normal_updated.csv')
Header_info_df = Header_info_df.dropna()
group = Header_info_df.groupby('studyUID')
image_info = list(group)
for study_details in image_info:
    try:
        sample_name = study_details[1][:1]['name'].tolist()[0]
        groupname = sample_name.split('\\')[2]
        # groupname = 'PDAC_test_CE'
        patient_info = name_patientID_info(sample_name)
        print(patient_info)
        create_json(study_details, groupname, patient_info[1]+'_'+patient_info[3])
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
        logger.debug('error at study', study_details)
        pass
