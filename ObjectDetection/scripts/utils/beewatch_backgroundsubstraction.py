import cv2
import numpy as np


def  bg_substraction_simple(video_path):
    cap = cv2.VideoCapture(video_path)

    _, first_frame = cap.read()

    while True:
        _, frame = cap.read()

        difference = cv2.absdiff(first_frame, frame)

        cv2.imshow("First frame", first_frame)
        cv2.imshow("Frame", frame)
        cv2.imshow("Difference", difference)

        key = cv2.waitKey(30)
        if key == 27:
            break
    cap.release()
    cap.destroyAllWindows()
    return cap

def  bg_substraction_gray(video_path):
    cap = cv2.VideoCapture(video_path)

    _, first_frame = cap.read()
    first_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
    #first_gray = cv2.GaussianBlur(first_gray,(5,5), 0)

    while True:
        _, frame = cap.read()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #gray_frame = cv2.GaussianBlur(gray_frame,(5,5), 0)


        difference = cv2.absdiff(first_gray, gray_frame)
        _, difference = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)

        cv2.imshow("First frame", first_frame)
        cv2.imshow("Frame", frame)
        cv2.imshow("Difference", difference)

        key = cv2.waitKey(30)
        if key == 27:
            break
    cap.release()
    cap.destroyAllWindows()
    return cap


cap = bg_substraction_gray('C:\\Data\\beeWatch\\temp\\Erlen_Hive_11_20190916_125421_540_M.mp4')

