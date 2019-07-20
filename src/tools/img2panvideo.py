"""
==========================================================================
Script:         Image 2 Panned Video
Description:    Generates a video of a higher resolution image scan to 
                simulate a camera scanning a surface for inspection.

Usage Example:
    python img2panvideo.py --input "../media/grieta-3.jpg" --width 400 --height 400 --scan_speed_x 4 --return_speed_x 16 --speed_y 4 --stride_y 64 --output "../media/wall-scan-slow.avi"
==========================================================================
"""

import argparse
import numpy as np
import cv2
import os
import sys



def process(input_image,output_width,output_height,scan_speed_x,return_speed_x,speed_y,stride_y,output_filename):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = 25.0
    out = cv2.VideoWriter(output_filename, fourcc, fps, (int(output_width), int(output_height)))
    img = cv2.imread(input_image)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)    
    state = 'start'

    src_image_w = int(img.shape[1])
    src_image_h= int(img.shape[0])

    print("Source image width:  %d pixels." % src_image_w)
    print("Source image height: %d pixels." % src_image_h)

    while state != 'finished':
        #print(state)
        if state == 'start':
            x0 = 0
            y0 = 0
            state = 'scan-row'
        elif state == 'scan-row':
            print("Horizontal scan at position %d/%d" % (y0,src_image_h))
            for x0 in range(0,int(img.shape[1])-output_width,scan_speed_x):
                x1 = x0 + output_width
                y1 = y0 + output_height
                subimg = img[y0:y1,x0:x1]    
                out.write(subimg)
            state = 'back-to-origin'
        elif state == 'back-to-origin':
            for x0 in range(int(img.shape[1])-output_width,0,-return_speed_x):
                x1 = x0 + output_width
                y1 = y0 + output_height
                subimg = img[y0:y1,x0:x1]    
                out.write(subimg)
            if (y0+stride_y) < (src_image_h-output_height):
                target_y0=y0 + stride_y           
                while y0<target_y0:
                    y0 = y0 + speed_y
                    y1 = y0 + output_height
                    subimg = img[y0:y1,x0:x1]    
                    out.write(subimg)
                state = 'scan-row'
            else:
                state = 'finished'            
    out.release()  



parser = argparse.ArgumentParser(description='Image to Panned Video')
parser.add_argument('--input', help='Input image filename',type=str)
parser.add_argument('--width', help='Output video frame with in pixels',type=int)
parser.add_argument('--height', help='Output video frame height in pixels',type=int)
parser.add_argument('--scan_speed_x', help='Horizontal displacement per frame',type=int)
parser.add_argument('--return_speed_x', help='Horizontal displacement per frame when returning to horizontal starting point.',type=int)
parser.add_argument('--speed_y', help='Vertical displacement per frame',type=int)
parser.add_argument('--stride_y', help='Vertical offset between each horizontal scan.',type=int)
parser.add_argument('--output', help='Generated video filename',type=str)
args = parser.parse_args()

# TODO: handle argument errors and ctrl+c
print("Generating %s." % args.output)
process(    
    args.input, 
    args.width,
    args.height,
    args.scan_speed_x,
    args.return_speed_x,
    args.speed_y,
    args.stride_y,
    args.output
)
print("Done.")


