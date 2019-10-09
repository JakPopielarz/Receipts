# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import cv2
import numpy as np

class Photo(Image.Image):
    def __init__(self, image_path):
        super().__init__()
        self.image = Image.open(image_path)
#        self.image.thumbnail((600, 600), Image.ANTIALIAS)
        self.bounding_rectangles = []
        self.samples = np.empty((0, 100))
        self.responses = []
        self.model = cv2.ml.KNearest_create()
        try:
            open("generalresponses.data")
            open("generalsamples.data")
            self.train()

            self.responses = self.responses.flatten()
            self.responses = self.responses.tolist()
        except FileNotFoundError:
            pass

    def crop_image(self, coordinates):
        self.image = self.image.crop(coordinates)

    def get_PIL(self):
        return self.image

    def change_image(self, image):
        self.image = image
#        self.image.thumbnail((600, 600), Image.ANTIALIAS)

    def create_contours(self):
#        self.image = ImageEnhance.Contrast(self.image).enhance(10)
#        self.image = self.image.filter(ImageFilter.SHARPEN)

        cv2_image = self.PIL_to_cv2()

        prepared_image = self.transform_cv2_image(cv2_image)
        self.contours = self.find_contours(prepared_image)

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

    def draw_contours(self, cv2_image):
        cv2.drawContours(cv2_image, self.contours, -1, (0, 255, 0), 1)

    def create_bounding_rectangles(self):
        for contour in self.contours:
            x, y, width, height = cv2.boundingRect(contour)
# TODO: Change the hard-coded 30
            if height > 30:
                self.bounding_rectangles.append([x, y, x+width, y+height])
        self.bounding_rectangles.sort(key=lambda x: x[0])

    def draw_bounding_rectangle(self, rectangle):
        draw = ImageDraw.Draw(self.image)
        draw.rectangle(rectangle, outline="magenta")

    def draw_bounding_rectangles(self):
        for rectangle in self.bounding_rectangles:
            draw = ImageDraw.Draw(self.image)
            draw.rectangle(rectangle, outline="magenta")
#        self.separate_bounding_rectangles()

    def separate_bounding_rectangles(self):
        self.image = ImageEnhance.Contrast(self.image).enhance(10000)
        image = self.image.filter(ImageFilter.SHARPEN)
        for rectangle in self.bounding_rectangles:
            rectangle[0] += 1
            rectangle[1] += 1
            cropped = image.crop(rectangle)
            name = str(rectangle[0])+".png"
            cropped.save(name)

    def prepare_sample(self, iteration):
        im = self.PIL_to_cv2()
        im = self.transform_cv2_image(im)

        rectangle = self.bounding_rectangles[iteration]

        roi = im[rectangle[1]:rectangle[3], rectangle[0]:rectangle[2]]
        roi_small = cv2.resize(roi, (10, 10))

        draw = ImageDraw.Draw(self.image)
        draw.rectangle(rectangle, outline="red")

        return roi_small

    def gather_answer(self, iteration):
        key = input("Digit: ")
        if key in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            self.responses.append(int(key))

        rectangle = self.bounding_rectangles[iteration]
        draw = ImageDraw.Draw(self.image)
        draw.rectangle(rectangle, outline="blue")

    def add_sample(self, roi):
        sample = roi.reshape((1, 100))
        self.samples = np.append(self.samples, sample, 0)

    def save_results(self):
        self.responses = np.array(self.responses, np.float32)
        self.responses = self.responses.reshape((self.responses.size, 1))
        print("training complete")

        np.savetxt('generalsamples.data', self.samples)
        np.savetxt('generalresponses.data', self.responses)

    def train(self):
        self.samples = np.loadtxt('generalsamples.data', np.float32)
        self.responses = np.loadtxt('generalresponses.data', np.float32)
        self.responses = self.responses.reshape((self.responses.size, 1))

        self.model.train(self.samples, cv2.ml.ROW_SAMPLE, self.responses)

    def recognize_digits(self):
        # Prepare image for recognition procedure
        image = self.PIL_to_cv2()
        image = self.transform_cv2_image(image)

        recognized = ""

        for rectangle in self.bounding_rectangles:
            # transform the image fragment with a digit
            roi = image[rectangle[1]:rectangle[3], rectangle[0]:rectangle[2]]
            roismall = cv2.resize(roi, (10, 10))
            roismall = roismall.reshape((1, 100))
            roismall = np.float32(roismall)

            # find nearest sample in knowledge-base
            _, results, _, _ = self.model.findNearest(roismall, k=1)
            # add the result to the end-result string
            recognized += str(int((results[0][0])))

        recognized = recognized[:-2]+","+recognized[-2:]

        return recognized
