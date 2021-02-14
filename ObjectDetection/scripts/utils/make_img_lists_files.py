
#%%
import shutil
import os
import time

#%%
#hives = ['Chueried_Hempbox', 'Chueried_Hive01']

hives = ['Chueried_Hempbox', 'Chueried_Hive01', 'ClemensRed', 'ClemensYellow',
        'Doettingen_Hive1', 'Echolinde', 'Echolinde_Night', 'Erlen_Hive04_diagonalview',
        'Erlen_Hive04_frontview', 'Erlen_Hive04_smartphone', 'Erlen_Hive11',
        'Erlen_Hive11_Night', 'Froh14', 'Froh23_TreeCavity', 'UnitedQueens']

folders = ['train', 'test', 'validate']

#%%
#source = 'P:\\object_detection\\labeling_new\\Froh23_TreeCavity\\frames\\rest_labelled_TO_DELETE_DUPPLICATES\\'
#dest_folder = 'P:\\object_detection\\labeling_new\\Froh23_TreeCavity\\frames\\'

dest_folder = 'C:\\Users\\glopez\\Google Drive\\yolo_models\\cfg_files\\list_of_files\\'

for hive in hives:
    for folder in folders:

        source_prefix = 'C:\\Users\\glopez\\Google Drive\\beeTracking_img_labeling\\'
        source_postfix = '\\' + folder + '\\'
        source = source_prefix + hive + source_postfix

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

        files = []
        files = os.listdir(source)

        print('all files: ', len(files))

        img_files = []
        img_files = [f for f in files if f[len(f)-3:len(f)] == 'jpg']
        print('img files: ', len(img_files))

        file_name = hive + '_'+ folder +'.txt'
        list_file = open(dest_folder + file_name, 'w')

        path_drive_prefix = '/content/gdrive/My Drive/beeTracking_img_labeling/'
        path_drive_sufix = '/'+ folder +'/'

        count = 0
        i = 0

        for item in img_files:
            #if count % 8 == 0:
            pd = path_drive_prefix + hive + path_drive_sufix + item
            list_file.write("%s\n" % pd)
            count += 1
            #list_file.write("%s\n" % item)

        list_file.close()
        print("finish list " + folder )

    print("finished " + hive)

print("finished")


# %%
