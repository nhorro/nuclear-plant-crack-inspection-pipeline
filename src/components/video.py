from IPython.display import SVG
from scipy import signal
import csv
import cv2
import sys

class VideoFileReader:
    """
    """
    
    def __init__(self,input_video,limit):        
        self.cap =  cv2.VideoCapture(input_video) 
        self.input_video_length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.input_video_width  = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.input_video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.input_video_fps    = self.cap.get(cv2.CAP_PROP_FPS)
        if limit > 0:
            self.max_frames_to_generate = limit
        else:
             self.max_frames_to_generate = self.input_video_length
        self.generated_frames = 0
        return
    
    def jump_to_frame(self,frame_number):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number-1)
        
    def get_max_frames_to_generate(self):
        return self.max_frames_to_generate
        
    def has_more_frames(self):
        return self.generated_frames < self.max_frames_to_generate

    def get_frame(self):
        return self.cap.read()
    
    def generated_frames_count(self):
        return self.generated_frames
        
    def next_frame(self):
        self.generated_frames = self.generated_frames + 1
    
    def get_dimensions(self):
        return self.input_video_width, self.input_video_height

    def get_total_frames(self):
        return self.input_video_length

    def get_fps(self):
        return self.input_video_fps

    def close(self):
        self.cap.release()


class VideoFileWriter:
    """
    """    
    def __init__(self,output_video,output_width,output_height): 
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = 25.0
        self.out = cv2.VideoWriter(output_video, fourcc, fps, (int(output_width), int(output_height)))
        
    def write(self,img):
        self.out.write(img)

    def close(self):
        self.out.release()



