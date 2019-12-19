# -*- coding: utf-8 -*-
"""
  Full Pipeline up to SpatioTemporalRegister
  Usage example:
    python crackcnnpipeline.py --jobs=jobs.json --name=wall-scan-slow

"""

import argparse
import json
import sys
from functools import reduce
sys.path.append("../../")
import os
import time
import numpy as np
import cv2

from components.spr import SQLiteSPR
from components.video import VideoFileReader
from components.cnn import CNNDetector
from components.motionestimation import VideoMotionEstimator
        
        
def process_pipeline(   input_video,
                        start_frame,
                        limit,
                        checkpoint_model,
                        class_names,
                        stride,
                        patch_size,
                        spr_output_filename ):
    """
        VIDEO --> VideoFileReader --> CNNDetector -------------> SQLiteSPR --> DB
                                  --> VideoMotionEstimator ---->
    """
    try:
        # 1. Instance VideoFileReader
        print("Opening video file %s." % input_video)
        vfr = VideoFileReader(input_video,limit)
        print("Starting on frame %d." % start_frame)
        vfr.jump_to_frame(start_frame)
        if limit > 0:
            print("Processing will be limited to %d frames." % limit)
        
        # 2, Instance VideoMotionEstimator
        print("Instancing Motion Estimator")
        me = VideoMotionEstimator()
         
        # 3. Instance CNNDetector   
        print("Instancing CNN Detector with model %s" % checkpoint_model)        
        cnnd = CNNDetector(
                checkpoint_model,
                input_shape=(patch_size,patch_size), 
                stride=(stride,stride),
                n_classes = len(class_names)
        )
        
        
        # 4. Instance SpatioTemporalRegister                    
        print("Instancing SPR and storing patches in %s" % spr_output_filename)        
        spr = SQLiteSPR()
        spr.open(spr_output_filename)
        spr.reset(class_names)
        width,height = vfr.get_dimensions()
        total_frames = vfr.get_total_frames()
        fps = vfr.get_fps()
        video_pk = spr.add_video(input_video,width,height,total_frames,fps)
        
        # Get first frame
        ret,frame1 = vfr.get_frame()
        
        # Set motion estimator to offset (0,0)
        x = np.zeros(2)
        
        while vfr.has_more_frames():
            # 1. Get next frame        
            vfr.next_frame()
            ret, frame2 = vfr.get_frame()
            
            print('Processing frame %d/%d [Progress: %d%%]' % 
                  (
                    vfr.generated_frames_count(), vfr.get_max_frames_to_generate(),
                    int((vfr.generated_frames_count()/vfr.get_max_frames_to_generate())*100.0)
                  ) 
            )
            if ret == False:
                break
            
            # 2. Register frame
            # TODO: vfr.generated_frames_count()/vfr.get_fps(), # Time
            frame_pk = spr.add_frame(
                    video_pk, 
                    vfr.generated_frames_count(), 
                    x[0], x[1]
            )
            
            # 3. Estimate motion
            dx = me.calculate_motion(frame1, frame2)
            x = x + dx
            
            # 4. Fix color encoding and scan image
            img = frame1.copy()
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Importante!!!
            cnnd.scan_image(img, spr.add_patch, frame_pk)
            
            # 5. Current frame is now previous frame
            frame1 = frame2
    except (KeyboardInterrupt, SystemExit):        
        spr.close()
        raise        
    spr.close()
            
def replace_path_expressions(filename,jobname,job):
  head, tail = os.path.split(filename)
  repls = ( '{checkpoint_model}', tail ), \
          ( '{name}', jobname), \
          ( '{date}', time.strftime("%Y_%m_%d") )
  return reduce(lambda a, kv: a.replace(*kv), repls, filename)
    
    
# Main
if __name__ == "__main__":    
    start_time = time.time()
    print("Processing started")
    
    parser = argparse.ArgumentParser(description='Image to Panned Video')
    parser.add_argument('--jobs', help='JSON with jobs training parameters',type=str)
    parser.add_argument('--name', help='Train job to execute ',type=str)
    args = parser.parse_args()

    with open(args.jobs, encoding='utf-8') as jobs_file:
        root = json.loads(jobs_file.read())
  
    job_name = args.name
    job = root["jobs"][job_name]

    spr_output_filename = replace_path_expressions(job["spr_output_filename"], job_name, job )
    print(spr_output_filename)
    try:
        process_pipeline(
            input_video=job["input_video"],
            start_frame=int(job["start_frame"]),
            limit=int(job["limit"]),
            checkpoint_model=job["checkpoint_model"],
            class_names = ("no_crack_prob","crack_prob"),
            stride=int(job["stride"]),
            patch_size=int(job["patch_size"]),
            spr_output_filename= spr_output_filename )
    except ( KeyboardInterrupt, SystemExit ):        
        print("Operation cancelled by user")

    end = time.time()
    elapsed = int(time.time() - start_time)
    print('Total running time: {:02d} hour(s), {:02d} minute(s), {:02d} second(s)'.format(
            elapsed // 3600, (elapsed % 3600 // 60), elapsed % 60)
    )