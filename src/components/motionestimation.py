
from scipy import signal
import numpy
import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys

class VideoMotionEstimator:
    def __init__(self,method='basic_phase_correlation'):        
        self.method = self.supported_methods[method]
    
    def calculate_motion(self, frame1, frame2):
        return self.method(self, frame1, frame2)
    
    def calculate_motion_basic_phase_correlation(self, frame1, frame2):
        dx = np.zeros(2)
        frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
        frame2_gray = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
        g_a = np.fft.fft2(frame1_gray)
        g_b = np.fft.fft2(frame2_gray)
        conj_b = np.ma.conjugate(g_b)
        r = g_a*conj_b
        r /= np.absolute(r)
        r = np.fft.ifft2(r)
        d = np.unravel_index(np.argmax(r), r.shape)        
        w = frame1.shape[0]
        h = frame1.shape[1]
        if d[1] > (h/2):
            dx[1] = d[1] - h
        else:
            dx[1] = d[1]           
        if d[0] > (w/2):
            dx[0] = d[0] - w
        else:
            dx[0] = d[0]        
        return dx
    
    supported_methods = {
        "basic_phase_correlation": calculate_motion_basic_phase_correlation
    }
