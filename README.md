clean_up_dcmfile.py —— 获取增强的原始数据

Run deeds BCV according to 
https://github.com/mattiaspaul/deedsBCV

Train CE based segmentation according to 
https://github.com/MIC-DKFZ/nnUNet

Train non-contrast based Segmentation with following 
https://github.com/MIC-DKFZ/nnUNet

CUDA_VISIBLE_DEVICES=1 nnUNet_train 2d nnUNetTrainerV2 502 0 --npz
CUDA_VISIBLE_DEVICES=1 nnUNet_train 3d_lowres nnUNetTrainerV2 502 0 --npz

preprocess_dcmfile.py——获取平扫数据的头文件信息

predict non-enhanced based segmentation with following 
CUDA_VISIBLE_DEVICES=1 nnUNet_predict -i /data/VPS/VPS_03/lmq/pancreas/PDAC_screening/data/data_train_val_ext/PDAC -o /data/VPS/VPS_03/lmq/pancreas/PDAC_screening/data/data_train_val_ext/label -t 502 -m 3d_lowres

precontrsat_preprocess.py —— 平扫数据分割预处理
classification_stack_swin_preprocess.py—— 准备分类数据集
PDAC_classification.ipynb ——分类模型训练

radiomics_seg_result.py —— 准备radiomics 结果
batchprocessing.py —— 影像组学获取组学结果的过程
segmentation_Radiomics.ipynb ——准备组学模型
README.md
# pancreas_screening
# pancreas_screening
