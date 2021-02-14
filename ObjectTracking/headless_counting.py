from datetime import datetime
from Tracking.iou_tracker import Tracker
from collections import OrderedDict
from collections import Counter
from tqdm import tqdm
import numpy as np
import sqlite3
import cv2

DB_PATH = '/Users/pascal/Coding/MP_bees/object_tracking/bees.db'
# PATH_TO_VIDEO = '/Users/pascal/Coding/MP_bees/simple_object_tracking/videos/Froh_23_20191013_075648_540_M.mp4'
# PATH_TO_VIDEO = '/Users/pascal/Coding/MP_bees/videos/bees_2.mp4'
PATH_TO_VIDEO = '/Users/pascal/Coding/MP_bees/object_tracking/videos/' \
                '118_Doettingen_Hive1_200820_gopro8_1080_200fps_W_short.mp4'
# ALT_PATH_TO_VIDEO = '/content/gdrive/My Drive/Bees/data/Froh_23_20191013_075648_540_M.mp4'
ALT_PATH_TO_VIDEO = '/content/gdrive/My Drive/Bees/data/high_fps/' \
                    '118_Doettingen_Hive1_200820_gopro8_1080_100fps_W_short.mp4'
RUN_ID = 28
PLOT = False


conn = sqlite3.connect(DB_PATH)
c = conn.cursor()


def get_coordinates_from_db(run_id, video, frame_nr):
    c.execute(
        "select * from coordinates where run_id = {} and video = '{}' and frame = {}".format(run_id, video, frame_nr))
    return c.fetchall()

cap = cv2.VideoCapture(PATH_TO_VIDEO)
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

dateTimeObj = datetime.now()
time_stamp = dateTimeObj.strftime("%d_%b_%Y_%H_%M_%S.%f")

skip_param = 8
fps = fps / skip_param
print(fps)

# dist_threshold, max_frame_skipped, max_trace_length, iou_threshold
if fps == 200:
    ct = Tracker(50, 20, 50, 0.5)
if fps == 100:
    ct = Tracker(100, 15, 50, 0.2)
if fps == 50:
    ct = Tracker(150, 10, 50, 0.005)
if fps == 25:
    ct = Tracker(250, 5, 50, 0.0025)

detections = []

# Create blank image for entrance contour detection

blank_image = np.zeros((height, width, 3), np.uint8)
blank_image[:, :] = (255, 255, 255)

img_center_x = width // 2 - 55
img_center_y = height // 2 - 20
# for united queens circle!
# cv2.circle(blank_image, (img_center_x, img_center_y), 135, (0, 0, 0), 5)
cv2.rectangle(blank_image, (660, 190), (1085, 260), (0, 0, 0),
              5)  # first tuple is the start, second tuple the end coordinates

gray = cv2.cvtColor(blank_image, cv2.COLOR_BGR2GRAY)
gray = cv2.bilateralFilter(gray, 11, 17, 17)
edged = cv2.Canny(gray, 200, 800, 1)
contours = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = contours[0] if len(contours) == 2 else contours[1]

traffic_dict = OrderedDict()
bee_in = 0
bee_out = 0
activity = ""

frame = 0
frame_counter = 0
all_tracks = {}
in_counted = []
out_counted = []

total_matches, total_no_matches = [], []

c.execute("select max(frame) from coordinates where run_id = {}".format(RUN_ID))
max_frame = c.fetchall()[0][0]

for frame in tqdm(range(1, max_frame, skip_param)):
    coordinates = get_coordinates_from_db(RUN_ID, ALT_PATH_TO_VIDEO, frame)
    frame_counter += 1

    rects = []
    for i in range(len(coordinates)):
        r_id, f_name, fr, b_id, xmin, xmax, ymin, ymax, X, Y, conf = coordinates[i]
        rects.append([xmin, ymin, xmax, ymax])

    objects, tracks, D, iou_scores, match, no_match = ct.update(rects)

    total_matches.append(match)
    total_no_matches.append(no_match)

    if PLOT:
        for key, values in tracks.items():
            if key not in all_tracks:
                all_tracks[key] = values
            else:
                all_tracks[key].append(values[-1])

    for (objectID, coordinates) in objects.items():
        if len(traffic_dict) == 0:
            traffic_dict[objectID] = []

        for cnt in contours:
            centroid_x = coordinates[0] + (coordinates[2] - coordinates[0]) // 2
            centroid_y = coordinates[1] + (coordinates[3] - coordinates[1]) // 2
            centroid = (centroid_x, centroid_y)
            res = cv2.pointPolygonTest(cnt, (centroid_x, centroid_y), False)
            traffic_dict[objectID].append(res)

            IN = False
            if res == 1 or res == 0:
                IN = True

        try:
            len(traffic_dict[objectID + 1])
        except KeyError:
            traffic_dict[objectID + 1] = []

    if len(traffic_dict) > 0:
        for tb_id, tb_value in traffic_dict.items():
            if len(tb_value) == 0:
                continue
            if tb_id not in objects:
                last_counter = Counter(tb_value[-20:])
                total_counter = Counter(tb_value)
                if tb_value[0] == -1 and total_counter[-1] >= fps // 20 and last_counter[1] >= fps // 20:
                    bee_in += 1
                    traffic_dict[tb_id] = []
                    activity = "Bee {} flew in".format(tb_id)
                    in_counted.append(tb_id)
                if tb_value[0] == 1 and total_counter[1] >= fps // 20 and last_counter[-1] >= fps // 20:
                    bee_out += 1
                    traffic_dict[tb_id] = []
                    activity = "Bee {} flew out".format(tb_id)
                    out_counted.append(tb_id)

    info = [("Frame", frame), ("FPS", fps), ("Last activity", activity), ("Nr of Bees", int(len(objects))),
            ("Out", bee_out),
            ("In", bee_in)]

    if frame_counter % 100 == 0:
        break
        print(info)
        print(traffic_dict)


if PLOT:
    for cnt in contours:
        cv2.drawContours(blank_image, [cnt], -1, (36, 255, 12), 2)


    disappeared = out_counted + in_counted
    for id in disappeared:
        if id in all_tracks.keys():
            for point in all_tracks[id]:
                if id in out_counted:
                    color = (255,0,0)
                elif id in in_counted:
                    color = (0,255,0)
                cv2.circle(blank_image, (point[0], point[1]), 1, color, -1)
            cv2.putText(blank_image, str(id), (point[0] - 30, point[1] + 30), 0, 0.7,
                            color, 1)
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(blank_image, text, (10, int(height) - ((i * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 0, 0),
                            1)


    import matplotlib.pyplot as plt
    fig1 = plt.figure()
    plt.imshow(blank_image)
    plt.show()
    fig1.savefig('example.png', dpi = 1000)

print(info)
conn.close()
