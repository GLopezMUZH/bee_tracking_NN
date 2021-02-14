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

skip_param = 1
fps = fps / skip_param
print(fps)

# ct = Tracker(50, (180+fps)/20, 50, (300+fps)/2000)

# dist_threshold, max_frame_skipped, max_trace_length, iou_threshold
if fps == 200:
    ct = Tracker(50, 20, 50, 0.5)
if fps == 100:
    ct = Tracker(100, 15, 50, 0.2)
if fps == 50:
    ct = Tracker(150, 10, 50, 0.005)
if fps == 25:
    ct = Tracker(250, 5, 50, 0.0025)

outname = 'output_videos/bee_output_{}_{}fps.avi'.format(time_stamp, fps)
fourcc = cv2.VideoWriter_fourcc(*"MJPG")
out = cv2.VideoWriter(outname, fourcc, 10.0, (int(width), int(height)))
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

c.execute("select max(frame) from coordinates where run_id = {}".format(RUN_ID))
max_frame = c.fetchall()[0][0]


for frame in tqdm(range(1, max_frame, skip_param)):

    ret, image_np = cap.read()
    if ret:
        cap.set(1, frame)
        rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        image_np_expanded = np.expand_dims(image_np, axis=0)
        coordinates = get_coordinates_from_db(RUN_ID, ALT_PATH_TO_VIDEO, frame)

        rects = []
        for i in range(len(coordinates)):
            r_id, f_name, fr, b_id, xmin, xmax, ymin, ymax, X, Y, conf = coordinates[i]
            rects.append([xmin, ymin, xmax, ymax])

        objects, tracks, D, iou_scores, match, no_match = ct.update(rects)

        for (objectID, coordinates) in objects.items():
            if len(traffic_dict) == 0:
                traffic_dict[objectID] = []

            for cnt in contours:
                centroid_x = coordinates[0] + (coordinates[2] - coordinates[0]) // 2
                centroid_y = coordinates[1] + (coordinates[3] - coordinates[1]) // 2
                centroid = (centroid_x, centroid_y)
                cv2.drawContours(image_np, [cnt], -1, (36, 255, 12), 2)
                res = cv2.pointPolygonTest(cnt, (centroid_x, centroid_y), False)
                traffic_dict[objectID].append(res)

                IN = False
                if res == 1 or res == 0:
                    IN = True

                # if not IN:
                cv2.circle(image_np, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
                cv2.putText(image_np, str(objectID), (centroid_x - 10, centroid_y - 20), 0, 0.5,
                            (255, 255, 255), 2)

                for center in tracks[objectID]:
                    x, y = center[0], center[1]
                    if not IN:
                        cv2.circle(image_np, (x, y), 1, (255, 255, 255), -1)
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
                    if tb_value[0] == 1 and total_counter[1] >= fps // 20 and last_counter[-1] >= fps // 20:
                        bee_out += 1
                        traffic_dict[tb_id] = []
                        activity = "Bee {} flew out".format(tb_id)

        info = [("Frame", frame), ("FPS", fps), ("Last activity", activity), ("Nr of Bees", int(len(objects))),
                ("Out", bee_out),
                ("In", bee_in)]
        # loop over the info tuples and draw them on our frame
        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(image_np, text, (10, int(height) - ((i * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 255, 0),
                        1)

        out.write(cv2.resize(image_np, (int(width), int(height))))

        # Display output
        cv2.imshow('', cv2.resize(image_np, (int(width), int(height))))
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    else:
        break

cap.release()
out.release()
cv2.destroyAllWindows()
conn.close()
