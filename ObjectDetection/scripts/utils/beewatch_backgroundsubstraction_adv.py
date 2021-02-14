import cv2
import numpy as np

video_path = 'C:\\Data\\beeWatch\\temp\\Erlen_Hive_11_20190916_125421_540_M.mp4'
cap = cv2.VideoCapture(video_path)

subtractor = cv2.createBackgroundSubtractorMOG2(history=5, varThreshold = 25, detectShadows = False) #120 frames moving window, reduction, filtering, morfological transformation and shadows

while True:
    _, frame = cap.read()

    mask = subtractor.apply(frame)

    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    key = cv2.waitKey(30)
    if key == 27:
        break
cap.release()
cap.destroyAllWindows()
