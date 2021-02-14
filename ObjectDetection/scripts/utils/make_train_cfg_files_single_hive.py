
#%%
import shutil
import os
import time

#%%
#hives = ['Chueried_Hempbox', 'Chueried_Hive01']

hives_120 = ['Chueried_Hive01', 'ClemensRed', 'ClemensYellow',
        'Echolinde', 'Echolinde_Night',
        'Erlen_Hive04_smartphone', 'Erlen_Hive11',
        'Erlen_Hive11_Night']

hives_240 = ['Chueried_Hempbox', 
        'Doettingen_Hive1',  'Erlen_Hive04_diagonalview',
        'Erlen_Hive04_frontview', 
        'Froh14', 'Froh23_TreeCavity', 'UnitedQueens']

nr_files_120 = [80]
nr_files_240 = [80]

hives = hives_120
nr_files = nr_files_120

#%%
dest_folder = 'C:\\Users\\glopez\\Google Drive\\yolo_models\\cfg_files\\yolo_train_files\\single_hive\\'

for hive in hives:

    for nr_to_save in nr_files:

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))


        file_name = hive + '.data'
        list_file = open(dest_folder + file_name, 'w')

        ln_train = "train = /content/gdrive/My\ Drive/yolo_models/cfg_files/list_of_image_files/" + hive + "_train_" + str(nr_to_save) + ".txt"
        ln_backup = "backup = /content/gdrive/My\ Drive/yolo_models/backup_yolo4/single_hive/" + hive + "/"

        list_file.write("classes = 1\n")
        list_file.write("%s\n" % ln_train)
        list_file.write("test = /content/gdrive/My\ Drive/yolo_models/cfg_files/all_test_20.txt\n")
        list_file.write("names = /content/gdrive/My\ Drive/yolo_models/cfg_files/bee.names\n")
        list_file.write("%s\n" % ln_backup)

        list_file.close()

    print("finished " + hive)

print("finished")


# %%
