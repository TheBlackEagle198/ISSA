import cv2
import numpy as np


class RoadDetector:
    def __init__(self, video_path):
        self.cam = cv2.VideoCapture(video_path)
        self.pts = None
        self.left_top = self.left_bottom = self.right_top = self.right_bottom = 0

    def convert_to_gray(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def create_mask(self, frame):
        mask = np.zeros_like(frame)
        height, width = frame.shape
        pt1 = (int(width * 0.57), int(height * 0.77)) # top right
        pt2 = (int(width * 0.45), int(height * 0.77)) # top left
        pt3 = (0, height) # bottom left
        pt4 = (width, height) # bottom right
        self.pts = np.array([pt1, pt2, pt3, pt4], dtype=np.int32) # pixel coords of the 4 points
        cv2.fillConvexPoly(mask, self.pts, 1)
        return mask

    def apply_mask(self, frame, mask):
        return cv2.multiply(frame, mask, dtype=cv2.CV_8U) # 8bit integer matrix

    # TODO: matrice blur ? elemente, valori, etc
    def display_big(self, frame):
        cv2.imshow('the main rrrroad', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cam.release()
            cv2.destroyAllWindows()

    def display_small(self, frame, window_name, size):
        frame = cv2.resize(frame, size)
        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cam.release()
            cv2.destroyAllWindows()

    def get_perspective_transform(self, frame):
        src_points = np.float32(self.pts)
        height, width = frame.shape
        dst_points = np.float32([(width, 0), (0, 0), (0, height), (width, height)]) # top right, top left, bottom left, bottom right
        M = cv2.getPerspectiveTransform(src_points, dst_points)
        return M

    def apply_perspective_transform(self, frame, M):
        height, width = frame.shape
        warped = cv2.warpPerspective(frame, M, (width, height))
        return warped

    def apply_blur(self, frame, ksize):
        return cv2.blur(frame, ksize)

    def apply_sobel(self, frame, ksize):
        frame = np.float32(frame)

        sobel_v = np.float32(
            [[-1, -2, -1],
             [ 0,  0,  0],
             [ 1,  2,  1]])
        sobel_h = np.transpose(sobel_v)

        grad_v = cv2.filter2D(frame, -1, sobel_v) # -1 depth - the same as source img - no of bits used to represent the color of a single pixel in the image; no of colors that it can represent
        grad_h = cv2.filter2D(frame, -1, sobel_h)

        grad = np.sqrt(grad_v ** 2 + grad_h ** 2)
        grad = cv2.convertScaleAbs(grad) # convert to 8bit integer matrix, bc the gradient can be negative too and pixels cant have negative values

        return grad

    def binarize_frame(self, frame, threshold): # threshold - intensity of filter
        _, binary_frame = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)
        return binary_frame

    def get_lane_markings(self, frame, threshold):
        height, width = frame.shape
        # for performance, i chose 3% instead of 5%
        frame[:, :int(width * 0.03)] = 0
        frame[:, int(width * 0.97):] = 0

        frame[int(height * 0.97):, :] = 0

        _, binary_frame = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)

        # apply opening operation
        kernel = np.ones((5, 5), np.uint8)
        binary_frame = cv2.morphologyEx(binary_frame, cv2.MORPH_OPEN, kernel) #remove white noise, dilation followed by erosion
        # separate the lane threshold into left and right halves
        left_half = binary_frame[:, :width // 2]
        right_half = binary_frame[:, width // 2:]
        # find coordinates of the white pixels that are part of the left and right half
        left_coordinates = np.argwhere(left_half == 255)
        right_coordinates = np.argwhere(right_half == 255)

        # extract x and y coordinates for the lines
        left_y, left_x = left_coordinates[:, 0], left_coordinates[:, 1]
        right_y, right_x = right_coordinates[:, 0], right_coordinates[:, 1] + width // 2

        return left_x, left_y, right_x, right_y

    def get_lane_lines(self, left_x, left_y, right_x, right_y):
        # apply regression to get the lane lines
        left_line = np.polynomial.polynomial.polyfit(left_y, left_x, deg=1) # polynomial regression of deg 1, aka y = ax + b
        right_line = np.polynomial.polynomial.polyfit(right_y, right_x, deg=1)
        return left_line, right_line


    def draw_birds_eye_view_lane_lines(self, frame, left_line, right_line):
        height, width = frame.shape

        y = np.array([0, height])

        # calculate the x coordinates for the left and right lines
        left_x = left_line[1] * y + left_line[0]
        right_x = right_line[1] * y + right_line[0]

        # create points for the left and right lines in the top-down view
        left_line_pts = np.float32([[left_x[0], y[0]], [left_x[1], y[1]]])
        right_line_pts = np.float32([[right_x[0], y[0]], [right_x[1], y[1]]])

        # draw the left and right lane lines
        cv2.line(frame, (int(left_line_pts[0][0]), int(left_line_pts[0][1])), (int(left_line_pts[1][0]), int(left_line_pts[1][1])), (200,0,0), 5)
        cv2.line(frame, (int(right_line_pts[0][0]), int(right_line_pts[0][1])), (int(right_line_pts[1][0]), int(right_line_pts[1][1])), (100,0,0), 5)

        return frame
    def draw_lane_lines(self, frame, left_line, right_line):
        height, width, _ = frame.shape

        y = np.array([0, height])

        # calculate the x coordinates for the left and right lines
        left_x = left_line[1] * y + left_line[0]
        right_x = right_line[1] * y + right_line[0]

        # create points for the left and right lines in the top-down view
        left_line_pts = np.float32([[left_x[0], y[0]], [left_x[1], y[1]]])
        right_line_pts = np.float32([[right_x[0], y[0]], [right_x[1], y[1]]])

        # apply inverse perspective transform to the line points
        M_inv = cv2.getPerspectiveTransform(np.float32([(frame.shape[1], 0), (0, 0), (0, frame.shape[0]), (frame.shape[1], frame.shape[0])]), np.float32(self.pts))
        left_line_pts = cv2.perspectiveTransform(np.array([left_line_pts]), M_inv)[0]
        right_line_pts = cv2.perspectiveTransform(np.array([right_line_pts]), M_inv)[0]

        # draw the left and right lane lines
        cv2.line(frame, (int(left_line_pts[0][0]), int(left_line_pts[0][1])), (int(left_line_pts[1][0]), int(left_line_pts[1][1])), (50, 50, 250), 5)
        cv2.line(frame, (int(right_line_pts[0][0]), int(right_line_pts[0][1])), (int(right_line_pts[1][0]), int(right_line_pts[1][1])), (50, 250, 50), 5)

        return frame

    def run(self):
        while True:
            ret, frame = self.cam.read()
            if ret is False:
                print("End of video")
                break
            gray = self.convert_to_gray(frame)
            self.display_small(gray, "gray", (320,240))
            mask = self.create_mask(gray)
            self.display_small(mask, "mask", (320,240))
            road = self.apply_mask(gray, mask)
            self.display_small(road, "road", (320,240))
            M = self.get_perspective_transform(road)
            top_down_view = self.apply_perspective_transform(road, M)
            self.display_small(top_down_view, "top_down_view", (320,240))
            #self.display_big(top_down_view)
            blurred_view = self.apply_blur(top_down_view, (3, 3))  # apply blur with a 3x3 kernel
            self.display_small(blurred_view, "blurred_view", (320,240))
            edge_view = self.apply_sobel(blurred_view, 3)
            self.display_small(edge_view, "edge_view", (320,240))
            binary_view = self.binarize_frame(edge_view, 80)
            self.display_small(binary_view, "binary_view", (320,240))
            binary_copy = binary_view.copy()
            # threshold the binary image to get the lane markings
            left_x, left_y, right_x, right_y = self.get_lane_markings(binary_copy, 200)
            if len(left_x) > 0 and len(right_x) > 0:  # check if left_x and right_x are existent
                left_line, right_line = self.get_lane_lines(left_x, left_y, right_x, right_y)
                frame_with_birds_eye_view_lanes = self.draw_birds_eye_view_lane_lines(top_down_view, left_line, right_line)
                self.display_small(frame_with_birds_eye_view_lanes, "frame_with_birds_eye_view_lanes", (320,240))
                frame_with_lanes = self.draw_lane_lines(frame, left_line, right_line)
                self.display_big(frame_with_lanes)



road_detector = RoadDetector('Lane Detection Test Video 01.mp4')
road_detector.run()