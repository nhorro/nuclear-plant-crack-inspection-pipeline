from scipy import signal
import csv
import numpy
import cv2
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
import numpy as np
import sqlite3 as sqlite
import sys



class CNNDetector:  
    """
    """
    def __init__(self, checkpoint_file, input_shape=(64,64), stride=(4,4), n_classes=2 ):
        """
        """
        self.input_shape = input_shape
        self.stride = stride
        self.model = load_model(checkpoint_file)        
        self.n_classes = n_classes # TODO: ver si hace falta
        
        
    def scan_image_file(self, filename):        
        img = cv2.imread(filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return self.scan_image(self, img)
        
    def scan_image(self, img, store_patch_callback, frame_pk):
        #boxes = []
        cell_width= self.input_shape[0]
        cell_height= self.input_shape[1]
        stride_x =  self.stride[0]
        stride_y = self.stride[1]

        for x0 in range(0,int(img.shape[1])-cell_width,stride_x):
            for y0 in range(0,int(img.shape[0])-cell_height,stride_y):            
                x1 = x0 + cell_width
                y1 = y0 + cell_height
                subimg = img[y0:y1,x0:x1]                
                subimg_converted = subimg.reshape(1,cell_width,cell_height,3) 
                prediction = self.model.predict(subimg_converted)   
                store_patch_callback(
                        frame_pk,
                        x0,y0,x1,y1,
                        tuple(prediction[0])
                )                
        
    def draw_found_bounding_boxes(self,img, boxes,color=(255,0,0)):
        for box in boxes:
            cv2.rectangle(img, box[0:2], box[2:4], color, 4)
        
    def get_keras_model():
        return self.model
