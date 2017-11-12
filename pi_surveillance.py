# Imports
from pyimagesearch.tempimage import TempImage
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
import imutils
import dropbox
import json
import time
import cv2

# arg parser
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True, help="Path to JSON Config")
args = vars(ap.parse_args())

# Filter warnings
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))
client = None

if conf["use_dropbox"]:
    client = dropbox.Dropbox(conf["dropbox_access_token"])
    print("[SUCCESS] dropbox account linked")
    
# Start cam
camera = PiCamera()
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

# Let camera warm up
print("[INFO] Warming up...")
time.sleep(conf["camera_warmup_time"])
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0

# Google Drive Initialization
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
gauth = GoogleAuth()
gauth.LoadCredentialsFile('mycreds.txt')
if gauth.credentials is None:
	gauth.LocalWebserverAuth() # Auth if no credentials
	gauth.SaveCredentialsFile('mycreds.txt')
elif gauth.access_token_expired:
	gauth.Refresh() # Refresh otherwise
else:
	gauth.Authorize() # Initialize
drive = GoogleDrive(gauth)

# Capture from camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = f.array # Grab frame as array
    timestamp = datetime.datetime.now()
    text = "Unoccupied"
    
    frame = imutils.resize(frame,width=500) # Resize image
    frame = cv2.flip(frame,0)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21,21),0)
    
    if avg is None: # If avg frame is None, initialize
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        rawCapture.truncate(0)
        continue
    cv2.accumulateWeighted(gray, avg,0.5) # Weighted avg b/w current frame and prior
    frameDelta = cv2.absdiff(gray,cv2.convertScaleAbs(avg)) # Difference between current frame and running average
    
    thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255, cv2.THRESH_BINARY)[1] # Threshold delta image
    thresh = cv2.dilate(thresh, None, iterations=2) # Dilate frame to fill in holes
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Find contours
    cnts = cnts[0]
##    cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    for c in cnts: # Loop over contours
        if cv2.contourArea(c) < conf["min_area"]: # Check if our contour is too small, and ignore
            continue
        (x,y,w,h) = cv2.boundingRect(c) # Bounding box of contour
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2) # Draw rectangle
        text = "Occupied"
    
    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p") # Timestamp generation
    cv2.putText(frame, "Room Status: {}".format(text),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255),2) 
    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0,0,255), 1)

    if text == "Occupied": # Check if room is occupied
        if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]: # Check if enough time has passed
            motionCounter +=1 # Increment counter
            
            if motionCounter >= conf["min_motion_frames"]: # Check if we have consistent motion
                if conf["use_dropbox"]: # Check if we're using dropbox upload
                    t = TempImage() # Make temp image
                    cv2.imwrite(t.path, frame)
                    
                    print("[UPLOAD] {}".format(ts))
                    path ="/{base_path}/{timestamp}.jpg".format(base_path=conf["dropbox_base_path"], timestamp=ts)
                    client.files_upload(open(t.path, "rb").read(),path) # Upload to Dropbox
                    t.cleanup()
                    
                if conf["use_drive"]:
                    filenameOut = "{timestamp}.jpg".format(timestamp=ts)
                    cv2.imwrite(filenameOut, frame)
                    
                    print("[UPLOAD] {}".format(ts))
                    imOut = drive.CreateFile()
                    imOut.SetContentFile(filenameOut)
                    imOut.Upload()
                    
                    
                lastUploaded = timestamp # Update the timestamp
                motionCounter = 0 # Update motion counter
                
    else: # Otherwise room is not occupied. Set to 0
        motionCounter = 0
            
    if conf["show_video"]: # Check if we enabled frame display
        cv2.imshow("Security Feed", frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord("q"):
            break
        
    rawCapture.truncate(0)
