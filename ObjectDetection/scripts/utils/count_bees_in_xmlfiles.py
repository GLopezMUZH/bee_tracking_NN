#%%
import pandas as pd
import xml.etree.ElementTree as ET
import os
import sqlite3
import time 


#%%
hives = ['Chueried_Hempbox', 'Chueried_Hive01', 'ClemensRed', 'ClemensYellow',
        'Doettingen_Hive1', 'Echolinde', 'Echolinde_Night', 'Erlen_Hive04_diagonalview',
        'Erlen_Hive04_frontview', 'Erlen_Hive04_smartphone', 'Erlen_Hive11',
        'Erlen_Hive11_Night', 'Froh14', 'Froh23_TreeCavity', 'UnitedQueens']





#%%
#hives = ['ClemensRed']
nr_bees_summary_file_path = 'C:\\Users\\glopez\\Google Drive\\beeTracking_img_labeling\\nr_bees_summary'
list_file = open(nr_bees_summary_file_path + '_test.txt', 'w')


#%%
for hive in hives:
    print("Start hive ", hive, ' at ' , time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    hive_name = hive
    nr_bees_hive = 0
    nr_files_counted = 0

    TXT_FILES_PATH = 'C:\\Users\\glopez\\Google Drive\\beeTracking_img_labeling\\' + hive + '\\test'
    txt_files_lst = []
    for filename in os.listdir(TXT_FILES_PATH):
        if not filename.endswith('.txt'): continue
        fullname = os.path.join(TXT_FILES_PATH, filename)
        txt_files_lst.append(fullname)

    for file_name in txt_files_lst:
        nr_bees_frame = len(list(open(file_name)))
        nr_files_counted += 1
        nr_bees_hive += nr_bees_frame

    print(len(txt_files_lst))
    list_file.write(hive + ', ' + str(len(txt_files_lst)) + ', ' + str(nr_files_counted) + ', ' + str(nr_bees_hive)  + '\n')

    print("finished ",hive)

list_file.close()
# %%
