# -*- coding: utf-8 -*-
import os
import sys
sys.path.append("../")

from spr import SQLiteSPR

class_names = ("crack_prob", "no_crack_prob")
probabilities = ( 0.5, 0.3 )

spr = SQLiteSPR()
spr.open("test2.db")
spr.reset(class_names)
video_pk=spr.add_video("test.avi",320,200,100,25)     
frame_pk=spr.add_frame(video_pk, 1, 10,20)
spr.add_patch(frame_pk, 10, 20, 30, 40, probabilities )
spr.close()
