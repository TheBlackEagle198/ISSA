import cv2
import numpy as np

def main() -> None:
    cam = cv2.VideoCapture('Lane Detection Test Video 01.mp4')

    bar_width = 30

    left_top = (int(0), int(0))
    left_bottom = (int(0), int(0))
    right_top = (int(0), int(0))
    right_bottom = (int(0), int(0))

    while True:
        ret, original_frame = cam.read()

        if not ret:
            print('Video ended')
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # cv2.imshow('Original', original_frame)
        # cv2.moveWindow('Original', 0, 0)

        # Exercise 2
        ratio = original_frame.shape[0] / original_frame.shape[1]
        width = 480
        resized_frame = cv2.resize(original_frame, (int(width), int(width * ratio)))

        cv2.imshow('Resized', resized_frame)
        cv2.moveWindow('Resized', 0, 0)

        # Exercise 3
        grayscale_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('Grayscale', grayscale_frame)
        cv2.moveWindow('Grayscale', width, 0)

        # Exercise 4
        width = grayscale_frame.shape[1]
        height = grayscale_frame.shape[0]
        upper_left = (int(width * 0.42), int(height * 0.77))
        upper_right = (int(width * 0.6), int(height * 0.77))
        lower_left = (int(0), int(height - 1))
        lower_right = (int(width - 1), int(height - 1))

        trapezoid_points = np.array([upper_left, upper_right, lower_right, lower_left], dtype='int32')

        trapezoid_frame = np.zeros((height, width), dtype='uint8')
        cv2.fillConvexPoly(trapezoid_frame, points=trapezoid_points, color=1)
        trapezoid_frame *= grayscale_frame

        cv2.imshow('Trapezoid', trapezoid_frame)
        cv2.moveWindow('Trapezoid', width * 2, 0)

        # Exercise 5
        screen_points = np.array([(0, 0), (width - 1, 0), (width - 1, height - 1), (0, height - 1)], dtype='float32')
        magical_matrix = cv2.getPerspectiveTransform(np.float32(trapezoid_points), screen_points)

        stretched_trapezoid_frame = cv2.warpPerspective(trapezoid_frame, magical_matrix, (width, height))

        cv2.imshow('Stretched Trapezoid', stretched_trapezoid_frame)
        cv2.moveWindow('Stretched Trapezoid', 0, int(width * ratio) + bar_width)

        # Exercise 6
        blured_frame = cv2.blur(stretched_trapezoid_frame, ksize=(3, 3))

        cv2.imshow('Blurred', blured_frame)
        cv2.moveWindow('Blurred', width, int(width * ratio) + bar_width)

        # Exercise 7
        sobel_vertical = np.float32([
            [-1, -2, -1],
            [ 0,  0,  0],
            [ 1,  2,  1]
        ])

        sobel_horizontal = np.transpose(sobel_vertical)

        frame_f = np.float32(blured_frame)

        frame_1 = cv2.filter2D(frame_f, -1, sobel_vertical)
        frame_2 = cv2.filter2D(frame_f, -1, sobel_horizontal)

        combined = np.sqrt(frame_1 * frame_1 + frame_2 * frame_2)

        sobel_frame = cv2.convertScaleAbs(combined)

        cv2.imshow('Sobel', sobel_frame)
        cv2.moveWindow('Sobel', width * 2, int(width * ratio) + bar_width)

        # Exercise 8
        threshold = int(120)

        binary_frame = np.array(sobel_frame > threshold, dtype='uint8')
        binary_frame *= 255
        cv2.imshow('Binary', binary_frame)
        cv2.moveWindow('Binary', 0, int(width * ratio * 2) + bar_width * 2)

        # Exercise 9
        # Remove the noise
        no_noise_frame = binary_frame.copy()
        margin = int(width * 0.08)
        no_noise_frame[0:height, 0:margin] = 0
        no_noise_frame[0:height, (width - margin): width] = 0
        no_noise_frame[height - int(0.03*height):height, 0:width] = 0
        cv2.imshow('No Noise', no_noise_frame)
        cv2.moveWindow('No Noise', width, int(width * ratio * 2) + bar_width * 2)

        # Find the coordinates of the white points
        left_xs = []
        left_ys = []
        right_xs = []
        right_ys = []

        half = int(width // 2)
        first_half = no_noise_frame[0:height, 0:half]
        second_half = no_noise_frame[0:height, half:width]
        cv2.imshow('First Half', first_half)
        cv2.imshow('Second Half', second_half)

        left_points = np.argwhere(first_half > 1) # stores the matrix coordinates of the white pixels
        right_points = np.argwhere(second_half > 1) # stores the matrix coordinates of the white pixels

        # since argwhere returns the coordinates reversed, this corrects that:
        for point in left_points:
            left_xs.append(point[1])
            left_ys.append(point[0])
        for point in right_points:
            right_xs.append(point[1] + half)
            right_ys.append(point[0])

        # Exercise 10
        lined_frame = binary_frame.copy()
        # draw the middle line
        cv2.line(lined_frame, (half, 0), (half, height), (100, 0, 0), 2)

        # find the line that best fits the left and right points
        b_left, a_left = np.polynomial.polynomial.polyfit(left_xs, left_ys, deg=1)
        b_right, a_right = np.polynomial.polynomial.polyfit(right_xs, right_ys, deg=1)

        left_top_y = int(0)
        left_top_x = int((left_top_y - b_left) / a_left)

        left_bottom_y = int(height - 1)
        left_bottom_x = int((left_bottom_y - b_left) / a_left)

        right_top_y = int(0)
        right_top_x = int((right_top_y - b_right) / a_right)

        right_bottom_y = int(height - 1)
        right_bottom_x = int((right_bottom_y - b_right) / a_right)
        
        if np.abs(left_top_x) < 10 ** 8 and np.abs(left_bottom_x) < 10 ** 8:
            left_top = (left_top_x, left_top_y)
            left_bottom = (left_bottom_x, left_bottom_y)

        if np.abs(right_top_x) < 10 ** 8 and np.abs(right_bottom_x) < 10 ** 8:
            right_top = (right_top_x, right_top_y)
            right_bottom = (right_bottom_x, right_bottom_y)

        # Draw the lines
        cv2.line(lined_frame, left_top, left_bottom, (200, 0, 0), 5)
        cv2.line(lined_frame, right_top, right_bottom, (100, 0, 0), 5)
        # Show the frame
        cv2.imshow('Binary with lines', lined_frame)
        cv2.moveWindow('Binary with lines', width * 2, int(width * ratio * 2) + bar_width * 2)

        # Exercise 11
        blank_frame_left = np.zeros((height, width), dtype='uint8')
        blank_frame_right = np.zeros((height, width), dtype='uint8')

        cv2.line(blank_frame_left, left_top, left_bottom, 255, 3)
        cv2.line(blank_frame_right, right_top, right_bottom, 255, 3)

        back_magic_matrix = cv2.getPerspectiveTransform(screen_points, np.float32(trapezoid_points))
        reverted_left_line = cv2.warpPerspective(blank_frame_left, back_magic_matrix, (width, height))
        reverted_right_line = cv2.warpPerspective(blank_frame_right, back_magic_matrix, (width, height))

        left_white_points = np.array(np.argwhere(reverted_left_line > 1))
        right_white_points = np.array(np.argwhere(reverted_right_line > 1))

        colored_img = resized_frame.copy()
        for y, x in left_white_points:
            colored_img[y, x] = [0, 0, 255]
        for y, x in right_white_points:
            colored_img[y, x] = [255, 0, 0]

        cv2.imshow('Colored Left Line', colored_img)


    cam.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()