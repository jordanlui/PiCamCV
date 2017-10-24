# Surveillance video with timestamp

from picamera import PiCamera
import datetime as dt
import time

def timeStamp():
    return dt.datetime.today().strftime('%Y-%m-%d-%H%M%S%f')

def record(recTime):
    
    camera = PiCamera()
    camera.rotation = 180
    camera.resolution = (1280, 720)

    camera.start_preview()
    camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    camera.start_recording(timeStamp() + '.h264')

    start = dt.datetime.now()
    while (dt.datetime.now() - start).seconds < recTime:
        camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        camera.wait_recording(0.2)
    camera.stop_recording()
    camera.stop_preview()

record(15)
