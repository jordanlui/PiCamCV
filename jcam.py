from picamera import PiCamera
from time import sleep
import datetime




camera = PiCamera()
camera.rotation = 180

def timeStamp():
    return datetime.datetime.today().strftime('%Y-%m-%d-%H%M%S%f')

def camCapture():
    filename = timeStamp() + '.jpg'
    camera.start_preview()
    camera.annotate_text = "Hello" + timeStamp()
    sleep(2)
    
    try:
        camera.capture(filename)
        camera.stop_preview()
        camera.close()
    except:
        print('error saving image')

def camBurst(numPhoto, interval):
    # Burst capture

    try:
        
        camera.start_preview(alpha=100)
        for i in range(numPhoto):
            camera.annotate_text = "Burst Photos"
            sleep(interval)
            camera.capture(filename)    

        camera.stop_preview()
        camera.close()

    except KeyboardInterrupt:
        print('Interrupted!')
        camera.stop_preview()
        camera.close()

def camVideo(t):
    camera.start_preview()
    filename = timeStamp() + '.h264'
    camera.start_recording(filename)
    sleep(t)
    camera.stop_recording()
    camera.stop_preview()

def highResPhoto():
    camera.resolution = (2592, 1944)
    camera.framerate = 15
    camera.start_preview()
    sleep(5)
    camera.capture(timeStamp()+'.jpg')
    camera.stop_preview()

# Main
try:
##    camBurst(5,0.2)
##    camVideo(10)
##    camCapture()
    camera.start_preview()
    for effect in camera.IMAGE_EFFECTS:
        camera.image_effect = effect
        camera.annotate_text = (str("Effect: {}".format(effect)))
        sleep(2)
    sleep(2)
    camera.stop_preview()


    
except:
    
    print('Error!')
    camera.stop_preview()
    camera.close()


# Ending

