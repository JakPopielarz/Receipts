# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import cv2
import numpy as np

class Photo(Image.Image):
    def __init__(self, image_path):
        super().__init__()
        self.image = Image.open(image_path)
        self.bounding_rectangles = []

    def crop_image(self, coordinates):
        self.image = self.image.crop(coordinates)

    def get_PIL(self):
        return self.image

    def change_image(self, image):
        self.image = image

    def draw_contours(self):
        cv2_image = self.PIL_to_cv2()

        prepared_image = self.transform_cv2_image(cv2_image)

        self.contours = self.find_contours(prepared_image)
        cv2.drawContours(cv2_image, self.contours, -1, (0, 255, 0), 1)

        self.cv2_to_PIL(cv2_image)

    def PIL_to_cv2(self):
        # load the image as a cv2 object
        self.image.save("tmp.png")
        cv2_image = cv2.imread("tmp.png")

        # clean up after conversion
        os.remove("tmp.png")

        return cv2_image

    def transform_cv2_image(self, cv2_image):
        # convert the image to grayscale
        gray = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)
        # blur the image to lose some imperfections and noise
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # convert the image to white things on a black background
        # contours can be found only on such image
        thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)

        return thresh

    def find_contours(self, prepared_image):
        _, contours, _ = cv2.findContours(prepared_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def cv2_to_PIL(self, cv2_image):
        # save the image with drawn contours, load it back as a PIL image
        cv2.imwrite("tmp.png", cv2_image)
        self.image = Image.open("tmp.png")

        # clean up after conversion
        os.remove("tmp.png")

    def create_bounding_rectangles(self):
        for contour in self.contours:
            x, y, width, height = cv2.boundingRect(contour)
#            if height > 30:
            self.bounding_rectangles.append([x, y, x+width, y+height])

    def draw_bounding_rectangles(self):
        for rectangle in self.bounding_rectangles:
            draw = ImageDraw.Draw(self.image)
            draw.rectangle(rectangle, outline="magenta")
        self.separate_bounding_rectangles()

    def separate_bounding_rectangles(self):
        self.image = ImageEnhance.Contrast(self.image).enhance(10000)
        image = self.image.filter(ImageFilter.SHARPEN)
        for rectangle in self.bounding_rectangles:
            rectangle[2] -= rectangle[0]
            rectangle[3] -= rectangle[1]
            rectangle[0] += 1
            rectangle[1] += 1
            cropped = image.crop(rectangle)
            name = str(rectangle[0])+".png"
            cropped.save(name)
#            self.detect_corners(name)
            

    def detect_corners(self, name):
        img = self.PIL_to_cv2()
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        
        gray = np.float32(gray)
        dst = cv2.cornerHarris(gray,2,3,0.04)
        
        #result is dilated for marking the corners, not important
        dst = cv2.dilate(dst,None)
        
        # Threshold for an optimal value, it may vary depending on the image.
        img[dst>0.01*dst.max()]=[0,0,255]
        
        cv2.imwrite("crn_"+name, img)
