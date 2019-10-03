# -*- coding: utf-8 -*-

from PIL import Image

class Photo(Image.Image):
    def __init__(self, image_path):
        super().__init__()
        self.image = Image.open(image_path)

    def get_PIL(self):
        return self.image
    
    def change_image(self, image):
        self.image = image
        