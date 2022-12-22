clean_up_dcmfile.py —— from origin file find out enhanced series and save them as for registration.

Run deeds BCV according to 
https://github.com/mattiaspaul/deedsBCV

Train CE based segmentation according to 
https://github.com/MIC-DKFZ/nnUNet

Train non-contrast based Segmentation with following 
https://github.com/MIC-DKFZ/nnUNet

CUDA_VISIBLE_DEVICES=1 nnUNet_train 2d nnUNetTrainerV2 502 0 --npz
CUDA_VISIBLE_DEVICES=1 nnUNet_train 3d_lowres nnUNetTrainerV2 502 0 --npz

preprocess_dcmfile.py—— from origin file find out non-enhanced series and save the for segmentation
precontrsat_preprocess.py —— preprocess non-enhanced series

predict non-enhanced based segmentation with following 
CUDA_VISIBLE_DEVICES=1 nnUNet_predict -i /data/VPS/VPS_03/lmq/pancreas/PDAC_screening/data/data_train_val_ext/PDAC -o /data/VPS/VPS_03/lmq/pancreas/PDAC_screening/data/data_train_val_ext/label -t 502 -m 3d_lowres

classification_stack_swin_preprocess.py—— preprocess nonenhanced and segmentation for image classification.
PDAC_classification.ipynb —— Train classification model

radiomics_seg_result.py —— prepare radiomics iamges
batchprocessing.py —— radiomics processing.
segmentation_Radiomics.ipynb ——train radiomics model
README.md
