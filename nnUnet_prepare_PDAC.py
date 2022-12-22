# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 16:34:04 2022

@author: liumingqian

with ce segmentation, prepare pancreas segmentation with precontrast images
load image list from the csv file created by PDAC_radiomics_preprocess.py
"""

import os
import SimpleITK as sitk
import pandas as pd
from sklearn.model_selection import train_test_split

output_path = 'E:\\Task502_PDAC_seg'
train_folder = 'imagesTr'
label_folder = 'labelsTr'
test_folder = 'imagesTs'
test_label = 'labelsTs'

if not os.path.exists(os.path.join(output_path,train_folder)):
    os.makedirs(os.path.join(output_path,train_folder))
    os.makedirs(os.path.join(output_path, label_folder))
    os.makedirs(os.path.join(output_path,test_folder))
    os.makedirs(os.path.join(output_path, test_label))

img_list_df = pd.read_csv("D:\\python_study\\pantric cancer\\PDAC_screening\\data\\segmentation_analysis.csv")
file_name = img_list_df['Image'].tolist()
file_label = img_list_df['GT'].tolist()

X_train, X_test, y_train, y_test = train_test_split(file_name, file_label, test_size=0.2, random_state=42)

k = 1        
for image_path in X_train: 
    print(image_path)
    try:
        train_name = 'PDAC_SEG'+ str(k).zfill(3) + '_0000.nii.gz'
        label_name = 'PDAC_SEG' + str(k).zfill(3) + '.nii.gz'
        train_image = sitk.ReadImage(image_path)
        dirname = os.path.dirname(image_path)
        label_path = dirname.replace('registered_images','segmentation')
        print(label_path+'_final_seg.nii')
        train_label = sitk.ReadImage(label_path+'_final_seg.nii.gz')
        print('sucessful load label')
        train_label.CopyInformation(train_image)
        sitk.WriteImage(train_image, os.path.join(output_path, train_folder,train_name))
        sitk.WriteImage(train_label, os.path.join(output_path, label_folder,label_name))
        k +=1
        print('sucessful processed', image_path)
    except:
        print('error with', image_path)
        pass

for image_path in X_test: 
    print(image_path)
    try:
        train_name = 'PDAC_SEG'+ str(k).zfill(3) + '_0000.nii.gz'
        label_name = 'PDAC_SEG' + str(k).zfill(3) + '.nii.gz'
        train_image = sitk.ReadImage(image_path)
        dirname = os.path.dirname(image_path)
        label_path = dirname.replace('registered_images','segmentation')
        train_label = sitk.ReadImage(label_path+'_final_seg.nii.gz')

        train_label.CopyInformation(train_image)
        sitk.WriteImage(train_image, os.path.join(output_path, test_folder,train_name))
        sitk.WriteImage(train_label, os.path.join(output_path, test_label,label_name))
        k +=1
        print('sucessful processed', image_path)
    except:
        print('error with', image_path)
        pass

file = open('data\\x_train.txt','w')
for i in range(len(X_train)):
    s = X_train[i]
    file.write(s)
file.close()

file = open('data\\x_train.txt','w')
for i in range(len(X_train)):
    s = X_train[i]
    file.write(s)
file.close()