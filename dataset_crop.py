import cv2
import numpy as np
import os


def apply_horizontal_vertical_kernel(filename):
    img = cv2.imread(filename, 0)
    (thresh, img_bin) = cv2.threshold(img, 128, 255,
                                      cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    img_bin = 255 - img_bin
    kernel_length = np.array(img).shape[1] // 40

    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))

    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))

    img_temp1 = cv2.erode(img_bin, vertical_kernel, iterations=3)
    vertical_lines_img = cv2.dilate(img_temp1, vertical_kernel, iterations=13)
    # cv2.imwrite("verticle_lines.jpg", vertical_lines_img)

    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
    horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=7)
    # cv2.imwrite("horizontal_lines.jpg", horizontal_lines_img)

    return vertical_lines_img, horizontal_lines_img


def choose_left_right_points(img):
    def scan_horizontally(start):
        flag = False
        for i in range(0, img.shape[1]//2-100):
           if img[start, i] == 255:
               print("left most line at ", i)
               flag = True
               break
        return flag, i

    def scan_horizontally_from_right(start):
        flag = False
        for j in range(img.shape[1] - 1, img.shape[1] // 2 - 100, -1):
            if img[start, j] == 255:
                print("right most line at ", j)
                flag = True
                break
        return flag, j
    flag, leftline_candidate = scan_horizontally(img.shape[0]//2)
    k = 100
    while flag != True:
        flag, leftline_candidate = scan_horizontally(k+img.shape[0]//2)
        k = k + 100
    left_most_line = leftline_candidate

    flag, rightline_candidate = scan_horizontally_from_right(img.shape[0]//2)
    k = 100
    while flag != True:
        flag, rightline_candidate = scan_horizontally_from_right(k+img.shape[0]//2)
        k = k + 100
    right_most_line = rightline_candidate

    mid_point = (left_most_line+right_most_line)//2
    return left_most_line, mid_point, right_most_line


def choose_top_bottom_points(img, mid_point):
    candidate_lines = []
    # for j in range(0, img.shape[0]):
    j = 0
    while j < (img.shape[0]):
        if img[j, mid_point] == 255:
            candidate_lines.append(j)
            while img[j, mid_point] == 255:
                j = j + 1
        j = j + 1

    print("horizontal lines are at positions =", candidate_lines)
    return candidate_lines


def crop_region_of_interest(filename, left_line, mid_line, right_line, list_of_horizontalines):
    if not os.path.exists("Cropped"):
        os.mkdir("Cropped")

    img = cv2.imread(filename)
    name = filename.split('.')[0]
    for i, each in enumerate(list_of_horizontalines):
        if i < len(list_of_horizontalines)-1:
            left_roi = img[each:list_of_horizontalines[i+1], left_line:mid_line, :]
            right_roi = img[each:list_of_horizontalines[i+1], mid_line:right_line, :]
            cv2.imwrite("Cropped/"+name+"L"+str(i)+".jpg", left_roi)
            cv2.imwrite("Cropped/"+name+"R"+str(i)+".jpg", right_roi)


if __name__ == "__main__":
    filename = "form2_600dpi.jpg"
    vertical_line_img, horizontal_line_img = apply_horizontal_vertical_kernel(filename)
    left_line, mid_line, right_line = choose_left_right_points(vertical_line_img)
    list_of_horizontalines = choose_top_bottom_points(horizontal_line_img, mid_line)
    crop_region_of_interest(filename, left_line, mid_line, right_line, list_of_horizontalines)