# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 21:47:10 2022

@author: liumingqian

list all file in the data_back,

move data to data, run python segmentation, save the results

"""


import os

import shutil

Data_path = '/data/VPS/VPS_03/lmq/PAII/panc_seg_deploy_weining/panc_seg_deploy_v0/data_HK_normal'
new_path = '/data/VPS/VPS_03/lmq/PAII/panc_seg_deploy_weining/panc_seg_deploy_v0/data'
output_path = '/data/VPS/VPS_03/lmq/PAII/panc_seg_deploy_weining/panc_seg_deploy_v0/results/segmentation'
processed_path = '/data/VPS/VPS_03/lmq/PAII/panc_seg_deploy_weining/panc_seg_deploy_v0/results/segmentation/data_processed'


file_list = os.listdir(Data_path)
for currentfile in file_list:
    try:
        print(currentfile)
        dest_path =  os.path.join(new_path, currentfile)
# if not os.path.exists(os.path.dirname(dest_path)):
# os.makedirs(os.path.dirname(dest_path))
        shutil.copytree(os.path.join(Data_path, currentfile), dest_path)
        os.system('rm -rf /data/VPS/VPS_03/lmq/PAII/panc_seg_deploy_weining/panc_seg_deploy_v0/results/converted_nii')
        os.system('sh /data/VPS/VPS_03/lmq/PAII/panc_seg_deploy_weining/panc_seg_deploy_v0/app/run_docker.sh')
        os.system('rm -rf /data/VPS/VPS_03/lmq/PAII/panc_seg_deploy_weining/panc_seg_deploy_v0/data/*')
        if os.path.exists(os.path.join(output_path,currentfile+'_final_seg.nii.gz')) == True:
            shutil.move(os.path.join(Data_path, currentfile), os.path.join(processed_path, currentfile))
            print('finish processing study ', currentfile)
        
    except:
        print('error at study', currentfile)
        pass
