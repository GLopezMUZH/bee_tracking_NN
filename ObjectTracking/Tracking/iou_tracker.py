# import the necessary packages
from scipy.spatial import distance as dist
#from kalmanFilter import KalmanFilter
from collections import OrderedDict
import numpy as np
from collections import deque
from scipy.optimize import linear_sum_assignment

np.set_printoptions(linewidth=220)

class Tracks(object):
    def __init__(self, detection, trackId):
        super(Tracks, self).__init__()
        # self.KF = KalmanFilter()
        # self.KF.predict()
        # self.KF.correct(np.matrix(detection).reshape(2, 1))
        self.trace = deque(maxlen=50)
        self.prediction = detection.reshape(1, 2)
        self.trackId = trackId
        self.skipped_frames = 0

    # def predict(self, detection):
    #     self.prediction = np.array(self.KF.predict()).reshape(1, 2)
    #     self.KF.correct(np.matrix(detection).reshape(2, 1))



class Tracker():
    def __init__(self, dist_threshold, max_frame_skipped, max_trace_length, iou_threshold):
        super(Tracker, self).__init__()
        self.dist_threshold = dist_threshold
        self.trace = deque(maxlen=max_trace_length)
        self.max_trace_length = max_trace_length
        self.iou_threshold = iou_threshold
        self.trackId = 0
        self.tracks = []
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.objects_trace = OrderedDict()
        self.disappeared = OrderedDict()
        self.maxDisappeared = max_frame_skipped

    def get_iou_score(self, box1: np.ndarray, box2: np.ndarray):
        """
        calculate intersection over union cover percent
        :param box1: box1 with shape (N,4) or (N,2,2) or (2,2) or (4,). first shape is preferred
        :param box2: box2 with shape (N,4) or (N,2,2) or (2,2) or (4,). first shape is preferred
        :return: IoU ratio if intersect, else 0
        """
        # first unify all boxes to shape (N,4)
        if box1.shape[-1] == 2 or len(box1.shape) == 1:
            box1 = box1.reshape(1, 4) if len(box1.shape) <= 2 else box1.reshape(box1.shape[0], 4)
        if box2.shape[-1] == 2 or len(box2.shape) == 1:
            box2 = box2.reshape(1, 4) if len(box2.shape) <= 2 else box2.reshape(box2.shape[0], 4)
        point_num = max(box1.shape[0], box2.shape[0])
        b1p1, b1p2, b2p1, b2p2 = box1[:, :2], box1[:, 2:], box2[:, :2], box2[:, 2:]

        # mask that eliminates non-intersecting matrices
        base_mat = np.ones(shape=(point_num,))
        base_mat *= np.all(np.greater(b1p2 - b2p1, 0), axis=1)
        base_mat *= np.all(np.greater(b2p2 - b1p1, 0), axis=1)

        # I area
        intersect_area = np.prod(np.minimum(b2p2, b1p2) - np.maximum(b1p1, b2p1), axis=1)
        # U area
        union_area = np.prod(b1p2 - b1p1, axis=1) + np.prod(b2p2 - b2p1, axis=1) - intersect_area
        # IoU
        if union_area.all():
            intersect_ratio = intersect_area / union_area
        else:
            intersect_ratio = 0

        return base_mat * intersect_ratio

    def register(self, coordinates):
        # coordinates in the format [xmin,ymin,xmax,ymax]
        self.objects[self.nextObjectID] = coordinates
        self.objects_trace[self.nextObjectID] = [self.get_centroid(coordinates)]
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1


    def deregister(self, objectID):
        del self.objects[objectID]
        del self.objects_trace[objectID]
        del self.disappeared[objectID]

    def get_centroid(self, coordinates):
        return (coordinates[0] + (coordinates[2] - coordinates[0]) // 2,
                coordinates[1] + (coordinates[3] - coordinates[1]) // 2)

    def get_min_distance_order(self, D):
        D_order = []
        for i in range(D.shape[1]):
            sorted_col = np.argsort(D[:, i])
            for j in range(D.shape[0]):
                if sorted_col[j] not in D_order:
                    D_order.append(sorted_col[j])
                    break
        return D_order

    def get_max_iou_order(self, iou_scores):
        I = np.absolute(np.array(iou_scores))
        I_order = []
        for i in range(I.shape[1]):
            sorted_col = np.argsort(-I[:, i])
            for j in range(I.shape[0]):
                if sorted_col[j] not in I_order:
                    I_order.append(sorted_col[j])
                    break
        return I_order

    def update(self, rects):
        no_match = []
        match = []
        D=[]
        iou_scores = []
        detections = []
        inputCoordinates = np.array(rects)
        if len(self.tracks) == 0:
            for i in range(np.array(rects).shape[0]):
                centroid = self.get_centroid(rects[i])
                track = Tracks(np.array(list(centroid)), self.trackId)
                detections.append(list(centroid))
                self.register(inputCoordinates[i])
                self.trackId += 1
                self.tracks.append(track)

        else:
            objectCoordinates = list(self.objects.values())
            if len(inputCoordinates) > len(objectCoordinates):
                d_row, d_col = linear_sum_assignment(dist.cdist(np.array(objectCoordinates), inputCoordinates,'euclidean'))
                for i,k in enumerate(inputCoordinates):
                    if i not in d_col:
                        self.register(inputCoordinates[i])

            objectIDs = list(self.objects.keys())
            objectCoordinates = list(self.objects.values())
            D = dist.cdist(np.array(objectCoordinates), inputCoordinates,'euclidean')
            iou_scores = []
            for o in objectCoordinates:
                iou_scores.append(self.get_iou_score(np.array(o), np.array(inputCoordinates)))
            iou_scores = np.array(iou_scores)

            # order the distance matrix along the main diagonal with smallest values
            D_order = self.get_min_distance_order(np.array(D))

            # order the IOU matrix along the main diagonal with largest values
            I_order = self.get_max_iou_order(iou_scores)

            # merge both orderings and see which makes more sense
            order = []
            for i in range(len(D_order)):
                if D_order[i] == I_order[i]:
                    order.append(D_order[i])
                else:
                    if np.max(iou_scores[I_order,:][i]) == 0:
                        order.append(D_order[i])
                    else:
                        order.append(I_order[i])

            usedRows = set()
            usedCols = set()



            for col, row in enumerate(order):
                if row in usedRows or col in usedCols:
                    continue

                if iou_scores[row, col] >= self.iou_threshold or D[row, col] <= self.dist_threshold:
                    # print('{} matched with {} with distance: {} and iou {}'.format(row, col, D[row,col], iou_scores[row,col]))
                    match.append((D[row,col], iou_scores[row,col]))
                    objectID = objectIDs[row]
                    self.objects[objectID] = inputCoordinates[col]
                    self.objects_trace[objectID].append(self.get_centroid(inputCoordinates[col]))
                    self.disappeared[objectID] = 0
                    usedRows.add(row)
                    usedCols.add(col)

                else:
                    # print('{} NOT matched with {} with distance: {} and iou {}'.format(row, col, D[row,col], iou_scores[row,col]))
                    no_match.append((D[row,col],iou_scores[row,col]))

                    pass

            unusedRows = set(range(0, iou_scores.shape[0])).difference(usedRows)
            unusedCols = set(range(0, iou_scores.shape[1])).difference(usedCols)

            if iou_scores.shape[0] >= iou_scores.shape[1]:
                for row in unusedRows:
                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)
            else:
                for col in unusedCols:
                    self.register(inputCoordinates[col])
        if len(D)>1:
            return self.objects, self.objects_trace, D[order], iou_scores[order], match, no_match
        else:
            return self.objects, self.objects_trace, [],[], [],[]
