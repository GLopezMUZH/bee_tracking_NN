import cv2
import numpy as np
import os
import glob

cwd = os.getcwd()
hives = glob.glob(cwd+'/*')
for hive in hives:
    videos = glob.glob(hive+"/videos/*.mp4")
    for video in videos:
        print(video)

        # Playing video from file:
        cap = cv2.VideoCapture(video)

        try:
            if not os.path.exists(hive+'/frames'):
                os.makedirs(hive+'/frames')
        except OSError:
            print('Error: Creating directory of data')

        currentFrame = 0
        while(True):
            currentFrame += 1
            ret, frame = cap.read()
            # % 35 because we have 5 mins of video * 60 seconds * 25 frames per second
            # this gives us a little bit more than 210 images per video
            if currentFrame % 35 == 0 or currentFrame == 1:

                # Saves image of the current frame in jpg file
                video_name = str(video.split('/')[-1].replace('.mp4',''))
                name = hive+'/frames/'+video_name+'_frame_'+ str(currentFrame) + '.jpg'
                print('Creating...' + name)
                try:
                    cv2.imwrite(name, frame)
                except:
                    break
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break


            # To stop duplicate images
        print("Next video")


        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()