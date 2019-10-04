# -*- coding: utf-8 -*-

from PIL import Image
import cv2
import os

class Photo(Image.Image):
    def __init__(self, image_path):
        super().__init__()
        self.image = Image.open(image_path)

    def get_PIL(self):
        return self.image
    
    def change_image(self, image):
        self.image = image

    def draw_contours(self):
        cv2_image = self.PIL_to_cv2()

        prepared_image = self.transform_cv2_image(cv2_image)

        contours = self.find_contours(prepared_image)
        cv2.drawContours(cv2_image, contours, -1, (0,255,0), 1)

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
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        # convert the image to white things on a black background
        # contours can be found only on such image
        thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)
        
        return thresh

    def find_contours(self, prepared_image):
        im2, contours, hierarchy = cv2.findContours(prepared_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def cv2_to_PIL(self, cv2_image):
        # save the image with drawn contours, load it back as a PIL image
        cv2.imwrite("tmp.png", cv2_image)
        self.image = Image.open("tmp.png")

        # clean up after conversion
        os.remove("tmp.png")
