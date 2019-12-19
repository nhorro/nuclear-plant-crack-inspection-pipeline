import sys
sys.path.append("../../components")

from videoinput.filevideoinput import VideoFileInputSource
from layers.videoprocessinglayers import VideoProcessingLayer
from layers.resizer import ResizerLayer
from layers.writer import WriterLayer
from layers.zmqpub import ZMQPubLayer
from videoprocessor import VideoProcessor

# Parameters
BASE_PATH="../../../"
INPUT_VIDEO_FILENAME = BASE_PATH+'media/wall-scan.avi'

ctx = {}

input_source = VideoFileInputSource( 
	filename=INPUT_VIDEO_FILENAME, start_frame=0, max_frames=None, repeat=True, interval=0.3 )
layers = [        
    ResizerLayer(OUTPUT_VIDEO_WIDTH,OUTPUT_VIDEO_HEIGHT),    
    ZMQPubLayer()
] 

vp = VideoProcessor()
vp.process_video( ctx, input_source, layers )