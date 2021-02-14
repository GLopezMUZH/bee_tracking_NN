
#%%
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
from copy import deepcopy
from numpy import genfromtxt
import pandas as pd
from time import gmtime, strftime

#%%
#VALIDATION_XML_DIRECTORY_PATH_PREFIX = '/content/gdrive/My Drive/yolo4_validation/' # leaky_activation mish_activation
VALIDATION_XML_DIRECTORY_PATH_PREFIX = 'C:\\Users\\glopez\\Google Drive\\yolo4_validation\\mish_activation\\'
#trained_model_type = 'single_hive' #single_hive #on_qty_of_train_images #individual_training
trained_model_types = ['single_hive', 'on_qty_of_train_images', 'individual_training', 'staged_2']

hives_120 = ['Chueried_Hive01', 'Chueried_Hive01_red70', 'Chueried_Hive01_green80'
        'ClemensRed', 'ClemensYellow',
        'Echolinde', 'Echolinde_Night',
        'Erlen_Hive04_smartphone', 
        'Erlen_Hive11', 'Erlen_Hive11_Night', 'Erlen_Hive11_grayscale', 'Erlen_Hive11_red70']

hives_240 = ['Chueried_Hempbox', 
        'Doettingen_Hive1',  'Erlen_Hive04_diagonalview',
        'Erlen_Hive04_frontview', 
        'Froh14', 'Froh23_TreeCavity', 'UnitedQueens']

nr_files_120 = [10, 20, 40, 80]
nr_files_240 = [10, 20, 40, 80, 160]

all_hives = hives_240.copy()
all_hives.extend(hives_120)


staged_2_models = ['Froh14_20_Chueried_Hive01','Chueried_Hive01_UnitedQueens', 'BeeWatch_Chueried_01_Erlen_Hive_11_Froh_23_UnitedQueens',
        'Erlen_Hive11_UnitedQueens', 'Erlen_Hive04_Hive11_UnitedQueens',
        'Doettingen_Echolinde_Erlen_UnitedQueens','Doettingen_Echolinde_Erlen_UnitedQueens_Froh14',
        'all_HD_hives_40']


#%%
validation_xml_directory_path = {}
i = 0

for trained_model_type in trained_model_types:
    if trained_model_type == 'on_qty_of_train_images':
        for hive in hives_120:
            for nr_to_save in nr_files_120:
                trained_model = trained_model_type + "/" + hive + "_" + str(nr_to_save)
                validation_xml_directory_path[trained_model] = VALIDATION_XML_DIRECTORY_PATH_PREFIX + trained_model_type + '\\' + hive + "_" + str(nr_to_save)
                #validation_xml_directory_path[trained_model] = VALIDATION_XML_DIRECTORY_PATH_PREFIX + trained_model_type + '/' + hive + "_" + str(nr_to_save)
                if not os.path.exists(validation_xml_directory_path[trained_model]):
                    i += 1
                    #print("WARNING, folder does not exist!!: ", validation_xml_directory_path[trained_model])
                    #os.makedirs(validation_xml_directory_path[hive])

        for hive in hives_240:
            for nr_to_save in nr_files_240:
                trained_model = trained_model_type + "/" + hive + "_" + str(nr_to_save)
                validation_xml_directory_path[trained_model] = VALIDATION_XML_DIRECTORY_PATH_PREFIX + trained_model_type + '\\' + hive + "_" + str(nr_to_save)
                if not os.path.exists(validation_xml_directory_path[trained_model]):
                    i += 1
                    #print("WARNING, folder does not exist!!: ", validation_xml_directory_path[trained_model])
                    #os.makedirs(validation_xml_directory_path[hive])

    elif (trained_model_type  == 'single_hive' or trained_model_type == 'individual_training'):
        for hive in all_hives:
            trained_model = trained_model_type + "/" + hive #+ "_" + trained_model_type
            validation_xml_directory_path[trained_model] = VALIDATION_XML_DIRECTORY_PATH_PREFIX + trained_model_type + '\\' + hive
            if not os.path.exists(validation_xml_directory_path[trained_model]):
                i += 1
    elif (trained_model_type == 'staged_2'):
        for m in staged_2_models:
            trained_model = trained_model_type + '/' + m
            validation_xml_directory_path[trained_model] = VALIDATION_XML_DIRECTORY_PATH_PREFIX + trained_model_type + '\\' + m

    
print("not existing folders: ", i)





# %%
# RESULTS PER MODEL AND HIVE
validation_results_per_model_and_hive = pd.DataFrame()
i = 0
missingfiles = 0

for k,v in validation_xml_directory_path.items():
    if os.path.exists(v):
        #results_file_path = v + '/validation_results_for_model.csv'
        results_file_path = v + '\\validation_results_per_hive.csv'
        if os.path.isfile(results_file_path):
            i += 1
            results_from_file = pd.DataFrame()
            results_from_file = pd.read_csv(results_file_path)
            validation_results_per_model_and_hive = validation_results_per_model_and_hive.append(results_from_file)
    else:
        missingfiles += 1


#validation_results_per_model.set_index("trained_model", inplace = True)
validation_results_per_model_and_hive.reset_index(drop=True)
print("existing files: ", i)
print("missing files: ", missingfiles)

#%%
# CALCULATE F-SCORE
# TODO

#%%
# Get best X models for hive
hive_top_models = validation_results_per_model_and_hive.sort_values(['hive_name','recall'], ascending=[True, False]).groupby('hive_name').head(38)

fname = VALIDATION_XML_DIRECTORY_PATH_PREFIX + 'hive_top_models_' + strftime("%y%m%d_%H%M", gmtime()) + '.csv'

hive_top_models.to_csv(fname)
print("finished")







#%%
# RESULTS AGGREGATED PER MODEL 
validation_results_per_model = pd.DataFrame()
i = 0
missingfiles = 0

for k,v in validation_xml_directory_path.items():
    if os.path.exists(v):
        #results_file_path = v + '/validation_results_for_model.csv'
        results_file_path = v + '\\validation_results_for_model.csv'
        #print(results_file_path)
        if os.path.isfile(results_file_path):
            i += 1
            results_from_file = pd.DataFrame()
            results_from_file = pd.read_csv(results_file_path)
            #results_from_file = genfromtxt(results_file_path, delimiter=',',dtype="U255,<i8,<i8,<i8,<i8,<i8,<i8,f8,f8",encoding="utf8", names = True)
            #print(results_from_file.flatten())
            validation_results_per_model = validation_results_per_model.append(results_from_file)
    else:
        missingfiles += 1

#validation_results_per_model.set_index("trained_model", inplace = True)
validation_results_per_model.reset_index(drop=True)
print("existing files: ", i)
print("missing files: ", missingfiles)

fname = VALIDATION_XML_DIRECTORY_PATH_PREFIX + 'models_performance_' + strftime("%y%m%d_%H%M", gmtime()) + '.csv'

validation_results_per_model.to_csv(fname)
print("finished")






