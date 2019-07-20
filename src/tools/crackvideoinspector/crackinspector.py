import time
import sys
sys.path.append("../../components")
import cv2



# GUI
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject,QThreadPool, QRunnable, QMetaObject,Qt
from mainwindow_ui import *


from video import VideoFileReader,VideoFileWriter
from spr import SQLiteSPRReader

class WorkerSignals(QObject):
    # Output signals
    video_loaded = QtCore.pyqtSignal(int,int,int,float) # w,h,total_frames, fps
    new_frame_available = QtCore.pyqtSignal(QtGui.QPixmap,int,int,int)



# Background thread
class BackgroundWorker(QRunnable):
    #finished_signal = QtCore.pyqtSignal()
    

    def __init__(self,start_frame=0, set_frame_to_next_crack=False):
        super(BackgroundWorker, self).__init__()        
        self.keep_running = True
        self.signals = WorkerSignals()
        self.input_video = "../../media/wall-scans/wall-scan-slow.avi"
        self.input_db = "../../products/spr-output-domingo17-feb2019.db"
        self.current_frame = start_frame
        self.set_frame_to_next_crack = set_frame_to_next_crack

    @QtCore.pyqtSlot(int)
    def run(self):       
        self.start_process()
        while self.keep_running == True:
            if False == self.process_frame():
                self.keep_running = False
        self.finish_process()            

    def stop(self):
        self.keep_running = False


    def jump_to_next_crack(self):
        self.current_frame = self.spr.get_frame_with_next_crack(self.current_frame)[0]
        self.vfr.jump_to_frame(self.current_frame)

    def start_process(self):

        self.vfr = VideoFileReader(self.input_video,0)
        self.spr = SQLiteSPRReader()
        self.spr.open(self.input_db)
        
        self.video_scale = 4
        self.video_width,self.video_height = self.vfr.get_dimensions()
        self.video_total_frames = self.vfr.get_total_frames()
        self.video_fps = self.vfr.get_fps()

        # TODO> hacer configurable
        self.vfw = VideoFileWriter(
                "output_frame_%d.avi" % self.current_frame, 
                    self.video_width*self.video_scale, 
                    self.video_height*self.video_scale )

        # Initial options
        self.vfr.jump_to_frame(self.current_frame)
        if self.set_frame_to_next_crack == True:
            self.jump_to_next_crack()
        
        # Notify
        self.signals.video_loaded.emit(
            self.video_width, self.video_height,
            self.video_total_frames,
            self.video_fps
        )

        

    def process_frame(self):
        if self.vfr.has_more_frames():
            ret, frame = self.vfr.get_frame()
            if ret == False:
                return False
            try:
                est_x,est_y = self.spr.get_estimated_offset_for_frame(self.current_frame+1)
                # Layers
                # ----------------------------------------------------------

                # FIXME: Ver resizing ajustado a ventana
                frame = cv2.resize(frame, (
                    self.video_width*self.video_scale,
                    self.video_height*self.video_scale), 
                    cv2.INTER_CUBIC 
                )     

                # L2. Original patches
                patches = self.spr.get_cracks(self.current_frame)
                for p in patches:
                    cv2.rectangle(
                        frame,
                        (
                            p[0]*self.video_scale,
                            p[1]*self.video_scale
                        ),
                        (
                            p[2]*self.video_scale,
                            p[3]*self.video_scale
                        ),
                        (0,0,255),
                        2
                    )

                # L3. Naive Bayes patches
                patches = self.spr.get_cracks_nb(est_x,est_y,36)
                for p in patches:
                    cv2.rectangle(
                        frame,
                        (
                            (p[0]-32)*self.video_scale,
                            (p[1]-32)*self.video_scale
                        ),
                        (
                            (p[0]+32)*self.video_scale,
                            (p[1]+32)*self.video_scale
                        ),
                        (0,255,0),
                        2
                    )
                    print(p)

                # l4. Clusters

                # L1. Video Motion Estimator
                cv2.putText( frame,
                    "Pos: (X:%d, Y:%d)" % (est_x,est_y),
                    (   
                        4,
                        (self.video_height-10)*self.video_scale
                    ), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.25*self.video_scale, 
                    (255,0,0),
                    2
                )

                # TODO: if capture enabled
                self.vfw.write(frame)

                frame = QtGui.QImage(
                    frame, 
                    frame.shape[1], frame.shape[0], 
                    frame.shape[1] * frame.shape[2], 
                    QtGui.QImage.Format_RGB888 )
                pixmap = QtGui.QPixmap()
                pixmap.convertFromImage(frame.rgbSwapped())                    
                self.signals.new_frame_available.emit(pixmap,self.current_frame,est_x,est_y)
                # END FIXME
                self.vfr.next_frame()
                self.current_frame = self.current_frame + 1
                has_more_frames = self.vfr.has_more_frames()
            except TypeError:
                has_more_frames = False
        return has_more_frames

    def finish_process(self):      
        self.spr.close()
        self.vfr.close()
        self.vfw.close()

        return



class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, threadpool,*args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.threadpool = threadpool

        self.setWindowTitle("Crack Video Footage Inspector v0.5 [Proof Of Concept]")

        # Video model
        self.video_current_frame = 0
        self.video_total_frames = 0

        self.playButton.clicked.connect(self.play_video)
        self.pauseButton.clicked.connect(self.stop_video)
        self.jumpToNextCrackButton.clicked.connect(self.jump_to_next_crack)
        self.videoSlider.valueChanged.connect(self.video_slider_changed)

        #spinNBThreeshold
        #cbMotionEstimator
        #cbPatches
        #cbNaiveBayes
        
    def show_frame(self,pixmap,current_frame,est_x,est_y):
        self.video_current_frame = current_frame
        self.curr_frame.setText("%d/%d" % (current_frame+1,self.video_total_frames))
        self.est_x.setText(str(est_x))
        self.est_y.setText(str(est_y))
        self.videoSlider.setValue(current_frame)
        self.videolabel.setPixmap(pixmap)

    def closeEvent(self, event):
        self.stop_video()  
        event.accept()


    # Video Player
    def video_slider_changed(self,):
        self.video_current_frame = self.videoSlider.value()

    def video_loaded(self,width,height,total_frames,fps):
        self.video_total_frames = total_frames
        self.videoSlider.setMinimum(1)
        self.videoSlider.setMaximum(self.video_total_frames)
        self.videoSlider.setValue(self.video_current_frame)

    def play_video(self, jump_to_next_crack=False):
        self.worker = BackgroundWorker(self.video_current_frame,jump_to_next_crack)
        self.worker.signals.video_loaded.connect(self.video_loaded)
        self.worker.signals.new_frame_available.connect(self.show_frame)        
        self.threadpool.start(self.worker)

    def stop_video(self): 
        self.worker.stop()

    # Crack Inspector
    def jump_to_next_crack(self):
        self.play_video(True)


if __name__ == "__main__":
    threadpool = QThreadPool()
    app = QtWidgets.QApplication([])
    window = MainWindow(threadpool=threadpool)
    window.show()
    app.exec_()
    print("Waiting for background process to finish")
    threadpool.waitForDone()
    print("Leaving gracefully")

 