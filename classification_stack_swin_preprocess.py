# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 13:55:08 2022

@author: liumingqian
"""
import SimpleITK as sitk
import numpy as np
import pandas as pd
import cv2
import os
import pandas as pd
import glob

'''
加载nifti格式的PDAC原始图像

加载nifti格式的pdac分割图像

'''
output_path = '/home/data/transformer_classification/extended_test'

# input_path= '//data/VPS/VPS_03/lmq/pancreas/PDAC_screening/data'


# input_image_pos = 'D:\\python_study\\pantric cancer'


'''
以二维图像为基准，匹配胰腺mask和肿瘤mask，
胰腺图像的灰度调整为-100到200HU，匹配他的二维相关mask和胰腺mask
'''
def load_all_image(input_image_path, input_label_path):
    train_image = sitk.ReadImage(input_image_path)
    train_label = sitk.ReadImage(input_label_path)
    train_label.CopyInformation(train_image)
    train_forground = train_image*sitk.Cast(train_label, train_image.GetPixelID())
    # train_label.CopyInformation(train_image)
    return train_forground, train_label



'''
根据region of interest 切割图像
'''
def threshold_based_crop_and_bg_median(image,mask):
    '''
    Use Otsu's threshold estimator to separate background and foreground. In medical imaging the background is
    usually air. Then crop the image using the foreground's axis aligned bounding box and compute the background 
    median intensity.
    Args:
        image (SimpleITK image): An image where the anatomy and background intensities form a bi-modal distribution
                                 (the assumption underlying Otsu's method.)
    Return:
        Cropped image based on foreground's axis aligned bounding box.
        Background median intensity value.
    '''
    # Set pixels that are in [min_intensity,otsu_threshold] to inside_value, values above otsu_threshold are
    # set to outside_value. The anatomy has higher intensity values than the background, so it is outside.
    inside_value = 0
    outside_value = 255
    bin_image = sitk.OtsuThreshold(image, inside_value, outside_value)

    # Get the median background intensity
    label_intensity_stats_filter = sitk.LabelIntensityStatisticsImageFilter()
    label_intensity_stats_filter.SetBackgroundValue(outside_value)
    label_intensity_stats_filter.Execute(bin_image,image)
    bg_mean = label_intensity_stats_filter.GetMedian(inside_value)
    
    # Get the bounding box of the anatomy
    label_shape_filter = sitk.LabelShapeStatisticsImageFilter()    
    label_shape_filter.Execute(bin_image)
    bounding_box = label_shape_filter.GetBoundingBox(outside_value)
    # The bounding box's first "dim" entries are the starting index and last "dim" entries the size
    return bg_mean, sitk.RegionOfInterest(image, bounding_box[int(len(bounding_box)/2):], bounding_box[0:int(len(bounding_box)/2)]), sitk.RegionOfInterest(mask, bounding_box[int(len(bounding_box)/2):], bounding_box[0:int(len(bounding_box)/2)])

'''
图像标准化
'''
def normalization(data):
    data = np.where(data<200, data, 200)
    data = np.where(data>-100, data, -100)
    M_m = np.max(data)-np.min(data)
    return(data-np.min(data))/M_m

'''
图像从sitk转为npy,保存为jpg
'''
def calculate_np_pos(img, mask):
    img_np = sitk.GetArrayFromImage(img)
    mask_np = sitk.GetArrayFromImage(mask)
    img_norm = normalization(img_np)
    img_mean, img_std = calculate_mean_std(img_norm)
    pan_np = np.where(mask_np<1, mask_np, 1)
    mask_mean, mask_std = calculate_mean_std(pan_np)
    pdac_mid_np = np.where(mask_np>1, mask_np, 0)
    pdac_np = np.where(pdac_mid_np<1, pdac_mid_np, 1)
    pdac_mean, pdac_std = calculate_mean_std(pdac_np)
    print('calculating statistics')
    mean_std_list = [img_mean, img_std, mask_mean, mask_std, pdac_mean, pdac_std]
    return img_norm, pan_np, pdac_np, mean_std_list

def calculate_mean_std(img_np):
    pixels = img_np[:,:,:].ravel()
    return np.mean(pixels), np.std(pixels)


'''
计算图像是阳性样本还是阴性样本,是否包含pancreas
'''
def mix_up_new_image(img_slice, mask_slice, pdac_slice):
    slice_shape = img_slice.shape
    # img3ch = np.zeros((slice_shape[0],slice_shape[1],3), dtype=np.float32)
    img3ch = np.array([img_slice, mask_slice[:slice_shape[0],:slice_shape[1]], pdac_slice[:slice_shape[0],:slice_shape[1]]])
    img3ch = img3ch.transpose(2,1,0)
    # img3ch[:,:, 0] = img_slice[:,:]*255
    # img3ch[:,:, 1] = mask_slice[c]*255
    #img3ch[:,:, 2] = pdac_slice[:slice_shape[0],:slice_shape[1]]*255
    return img3ch, pdac_slice.max(), mask_slice.max()
    
'''
生成一个包含阴性样本、阳性样本
image另存在文件夹中， 路径：/pos/文件名/1.jpeg
根据路径 生成dataframe， [路径，是否有胰腺分割，是否有胰腺癌分割]

使用CE segment的结果，生成同样的img label

最后生成的报告需要通过csvfile来挑选有pancreas的图像作为训练数据集，

待处理的目标文件包括train_extra和data_testHK
最后生成的file需要包括GT_result
'''
label_df = pd.DataFrame()
label_list = []
img_mean_std_df = pd.DataFrame()
all_mean_std = []


precontrast_result = pd.read_csv('extended test image.csv')
pdac_file_list = precontrast_result['Image'].values.tolist()
pdac_seg_list = precontrast_result['Mask'].values.tolist()
# pdac_seg_list = [x.replace('radiomics','results') for x in pdac_seg_list]

for i in range(len(pdac_file_list)):
    input_image_path = pdac_file_list[i]
    input_label_path = pdac_seg_list[i]
    file_name = input_image_path.split('/')[-1]
    # class_name = input_image_path.split('/')[-2]
    print('processing', file_name.strip('.nii.gz'))
    try:
        img, mask = load_all_image(input_image_path, input_label_path)
        _, img_crop, mask_crop = threshold_based_crop_and_bg_median(img, mask)
        img_norm, pan_np, pdac_np, mean_std_list = calculate_np_pos(img_crop, mask_crop)
        img_shape = img_norm.shape
        print(mean_std_list, img_shape)
        all_mean_std.append(mean_std_list)
        for i in range(img_shape[0]):
            img_slice = img_norm[i,: ,:]*255
            mask_slice = pan_np[i,:,:]*255
            pdac_slice = pdac_np[i,:,:]*255
            img3ch, pdac_slice_max, mask_slice_max = mix_up_new_image(img_slice, mask_slice, pdac_slice)
            path= os.path.join(output_path, file_name.strip('.nii.gz'))
            # print(path)
            if not os.path.exists(path):
                os.makedirs(path)
            cv2.imwrite(os.path.join(path, str(i)+'.jpeg'), img3ch) 
            label_list.append([os.path.join(path, str(i)+'.jpeg'), pdac_slice_max, mask_slice_max])
    except:
        pass

print(np.mean(all_mean_std, axis=0))

# label_df = pd.DataFrame(label_list, columns=['file_path','pdac_result','mask_result'])
# label_df.to_csv('image_label_extended.csv')

