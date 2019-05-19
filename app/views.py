from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.views.decorators.gzip import gzip_page
import threading
import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
CLASSES = ["face", "eye"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# Create your views here.
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640); 
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480);
        self.video.set(cv2.CAP_PROP_SATURATION,0.2);
        (_, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        return self.frame

    def update(self):
        while True:
            (_, self.frame) = self.video.read()

def gen(cam):
    while True:
        frame = cam.get_frame()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
             cv2.rectangle(frame,(x,y),(x+w,y+h),COLORS[0],2)
             cv2.putText(frame, CLASSES[0], (x, y),\
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[0], 2)
             #only fecth face area to detect eyes
             face_gray = gray[y:y+h, x:x+w]
             face_color = frame[y:y+h, x:x+w]
             eyes = eye_cascade.detectMultiScale(face_gray)
             for (ex,ey,ew,eh) in eyes:
                 cv2.rectangle(face_color,(ex,ey),(ex+ew,ey+eh),COLORS[1],2)
                 cv2.putText(face_color, CLASSES[1], (ex, ey),\
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[1], 2)

        _, frame= cv2.imencode('.jpg', frame)
        frame = frame.tobytes()

        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@gzip_page
def livestream(request):
    cam = VideoCamera()
    try:
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        print('Unable to load camera.')
