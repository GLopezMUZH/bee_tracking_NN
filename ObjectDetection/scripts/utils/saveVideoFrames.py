#%%
import cv2
import os
from time import gmtime, strftime   

""" 
PATH_TO_VIDEO = 'P:\\videos\\Erlen_Hive_04\\Erlen Hive 4 200410 von Smartphone Samsung Note 8\\Erlen_Hive_04_samsung_20200410_153124.mp4'
"""

PATH_TO_VIDEO = 'C:\\Users\\glopez\\Google Drive\\beeTracking_img_labeling\\Doettingen_Hive1\\videos\\Doettingen_Hive_1_M_Rec_20200427_171545_540_M.mp4'
folder_train = 'C:\\Data\\beeWatch\\temp\\Doettingen_Hive1\\frames\\' 
folder_test = 'C:\\Data\\beeWatch\\temp\\Doettingen_Hive1\\frames\\' 
folder = folder_train 
vidcap = cv2.VideoCapture(PATH_TO_VIDEO)
success,image = vidcap.read()
count = 0
i_train = 0
i_test = 0
saved = 0

print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))

#%%
while success:
    i_train += 1
    i_test += 1
    if i_train == 140:
        cv2.imwrite(os.path.join(folder_train,"Doettingen_Hive_1_M_Rec_20200427_171545_540_M_%d.jpg" % count), image) # save frame as JPEG file      
        i_train = 0
        saved += 1
    """
    if i_test == 90: #count % 7 == 0:
        cv2.imwrite(os.path.join(folder_test,"ClemensHiveRed_6421_%d.jpg" % count), image) # save frame as JPEG file      
        i_test = 0
    """
    success,image = vidcap.read()
    count += 1

#    if cv2.waitKey(25) & 0xFF == ord('q'):
#        break    

print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
print('Nr frames: ', count)


#%%
# GET EXIF ORIENTATION
from PIL import Image, ExifTags
frame_path_flipped = 'C:\\Users\\glopez\\Google Drive\\beeTracking_img_labeling\\Chueried_Hempbox\\train\\Chueried_Hempbox_frame_1000.jpg'
frame_path_ok = 'C:\\Users\\glopez\\Google Drive\\beeTracking_img_labeling\\Echolinde\\train\\Rec_20200603_054012_410_M_frame_3785.jpg'
frame_path_ok = 'C:\\Users\\glopez\\Google Drive\\beeTracking_img_labeling\\Erlen_Hive04_smartphone\\train\\Erlen_Hive_04_samsung_20200410_153124_1538.jpg'
frame_path_ok = 'C:\\Users\\glopez\\Google Drive\\beeTracking_img_labeling\\Froh14\\train\\Froh14_2020-07-14-23h02m08s335.jpg'
frame_path_ok = 'C:\\Users\\glopez\\Google Drive\\beeTracking_img_labeling\\UnitedQueens\\train\\united_queens_20190930-130100-1569841260_frame_120.jpg'

#frame_path_ok = 'C:\\Users\\glopez\\Google Drive\\beeTracking_img_labeling\\Doettingen_Hive1\\train\\Doettingen_Hive_1_M_Rec_20200427_045603_540_M_frame_153.jpg'


try:
    image=Image.open(frame_path_ok)

    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation]=='Orientation':
            print("break")
            break
    
    exif = image._getexif()


    print("img: ", frame_path_ok)
    print("exif: ",exif)

    print(exif[orientation])
    image.close()

    """
    image=Image.open(frame_path_ok)

    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation]=='Orientation':
            print("break")
            break
    
    exif = image._getexif()

    print(exif[orientation])


    if exif[orientation] == 3:
        image=image.rotate(180, expand=True)
    elif exif[orientation] == 6:
        image=image.rotate(270, expand=True)
    elif exif[orientation] == 8:
        image=image.rotate(90, expand=True)

    image.save(filepath)
    """
    #image.close()
except (AttributeError, KeyError, IndexError):
    # cases: image don't have getexif
    pass


# %%
