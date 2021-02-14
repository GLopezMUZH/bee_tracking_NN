import cv2
import os
from time import gmtime, strftime   
PATH_TO_VIDEO = 'P:\\videos\\Erlen_Hive_04\\Erlen Hive 4 200410 Reolink C2 Pro\\Erlen_Hive_04_200410_rl_c2pro_M\\diagonal left view\\Erlen_Hive_04_rl_c2pro_Rec_20200410_142258_540_M.mp4'
folder_train = 'P:\\object_detection\\labeling_new\\to_be_labeled\\Erlen_Hive_4\\diagonal_left_view\\train\\' 
folder_test = 'P:\\object_detection\\labeling_new\\to_be_labeled\\Erlen_Hive_4\\diagonal_left_view\\test\\' 
folder = folder_train

PATH_TO_VIDEO


for video in videos:
    print(video)

    vidcap = cv2.VideoCapture(PATH_TO_VIDEO)
    success,image = vidcap.read()
    count = 0
    i_train = 0
    i_test = 0

    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    while success:
        i_train += 1
        i_test += 1
        if i_train == 144:
            cv2.imwrite(os.path.join(folder_train,"Erlen_Hive_04_rl_c2pro_Rec_20200410_142258_540_M_%d.jpg" % count), image) # save frame as JPEG file      
            i_train = 0
        if i_test == 3501: #count % 7 == 0:
            cv2.imwrite(os.path.join(folder_test,"Erlen_Hive_04_rl_c2pro_Rec_20200410_142258_540_M_%d.jpg" % count), image) # save frame as JPEG file      
            i_test = 0
        success,image = vidcap.read()
        count += 1

    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
print('Nr frames: ', count)