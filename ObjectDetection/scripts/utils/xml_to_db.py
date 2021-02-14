#%%
import pandas as pd
import xml.etree.ElementTree as ET
import os
import sqlite3
import time 

#%%
conn = sqlite3.connect('C:\\Users\\glopez\\uzh_stuff\\beewatch_yolo\\bees.db')
#conn = sqlite3.connect('C:\\Users\\glopez\\Google Drive\\\yolo4_validation\\bees.db')
c = conn.cursor()

#%%
#c.execute("drop table validation_ground_truth")

#%%
createTable = False
if createTable:
    c.execute("""create table training_train_set_ground_truth (
                hivename text,
                filename text,
                width integer,
                height integer,
                xmin integer,
                xmax integer,
                ymin integer,
                ymax integer,
                x_center integer,
                y_center integer
    )""")

#%%
hives = ['Chueried_Hempbox', 'Chueried_Hive01', 'ClemensRed', 'ClemensYellow',
        'Doettingen_Hive1', 'Echolinde', 'Echolinde_Night', 'Erlen_Hive04_diagonalview',
        'Erlen_Hive04_frontview', 'Erlen_Hive04_smartphone', 'Erlen_Hive11',
        'Erlen_Hive11_Night', 'Froh14', 'Froh23_TreeCavity', 'UnitedQueens']

#%%
hives = ['Chueried_Hive01_green80']


for hive in hives:
    print("Start hive ", hive, ' at ' , time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    hive_name = hive 

    XML_FILES_PATH = 'C:\\Users\\glopez\\Google Drive\\beeTracking_img_labeling\\' + hive + '\\validate'
    xml_lst = []
    for filename in os.listdir(XML_FILES_PATH):
        if not filename.endswith('.xml'): continue
        fullname = os.path.join(XML_FILES_PATH, filename)
        xml_lst.append(fullname)

    dfcols = ['hive_name','filename', 'width', 'height', 'xmin','xmax','ymin','ymax','x_center','y_center']
    df = pd.DataFrame(columns=dfcols)


    for xml in xml_lst:
        etree = ET.parse(xml)
        root = etree.getroot()

        filename = root.find('filename').text
        size = root.find('size')
        width = int(size.find('width').text)
        height = int(size.find('height').text)
        objects = root.findall('object')
        for object in objects:
            box = object.find('bndbox')
            xmin = int(box.find('xmin').text)
            ymin = int(box.find('ymin').text)
            xmax = int(box.find('xmax').text)
            ymax = int(box.find('ymax').text)
            x = (xmin + xmax) // 2
            y = (ymin + ymax) // 2
            df = df.append(
                pd.Series([hive_name,filename,width,height,xmin,xmax,ymin,ymax,x,y],index = dfcols), ignore_index=True)

    df.head()

    df.to_sql("validation_ground_truth", conn, if_exists='append', index=False)
    print("finished")
conn.close()
# %%
