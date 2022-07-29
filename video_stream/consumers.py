# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import numpy as np
import cv2
from PIL import Image
import base64
from io import BytesIO

from os.path import dirname, join
from django.conf import settings

import os

import imutils

PREFERED_FPS=30
FRAME_DELAY=1/PREFERED_FPS
global NCLIENTS, broadcast_task, cap
NCLIENTS=0
cap = cv2.VideoCapture('video.mp4')

def capture_and_process(cap=cap):
    """Capture frame from video source and process."""
    # Capture frame-by-frame
    """frame_got, frame = cap.read()
    if frame_got is False:
        return None
    
    # frame processing
    ret = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # ..

    return ret"""
    protopath = join(dirname(__file__), "models/MobileNetSSD_deploy.prototxt")
    modelpath = join(dirname(__file__), "models/MobileNetSSD_deploy.caffemodel")
    detector = cv2.dnn.readNetFromCaffe(prototxt=protopath, caffeModel=modelpath)

    
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
            "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
            "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
            "sofa", "train", "tvmonitor"]

    while True:
            ret, frame = cap.read()
            frame = imutils.resize(frame, width=640, height=480)

            (H, W) = frame.shape[:2]

            blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
            detector.setInput(blob)
            person_detections = detector.forward()
       

            for i in np.arange(0, person_detections.shape[2]):
                idx = int(person_detections[0, 0, i, 1])
                confidence = person_detections[0, 0, i, 2]
                if confidence > 0.4:
                    idx = int(person_detections[0, 0, i, 1])

                if CLASSES[idx] != "person":
                    continue
                person_box = person_detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                
                for(W, H, W, H) in person_box[True]:
        
                    w1 = W - 150
    
                    if w1 < 0:
                        w1 = 0
    
                    w2 = W + 150
    
                    if w2 > 640:
                        w2 = 640
        
                    h1 = H - 150
    
                    if h1 < 0:
                        h1 = 0
    
                    h2 = H + 150
        
                    if h2 > 480:
                        h2 = 480
    
                    pts1 = np.float32([[w1,h1],[w2,h1],[w1,h2],[w2,h2]])
                    pts2 = np.float32([[0,0],[640,0],[0,480],[640,480]])

                    M = cv2.getPerspectiveTransform(pts1,pts2)

                    img = cv2.warpPerspective(frame,M,(640,360))

                    ret, frame = cv2.imencode('.jpg', img)
                    return frame.tobytes()

async def broadcast_task(channel_layer, room_group_name):
    print('*********Start broadcasting..')
    while True:
        await asyncio.sleep(FRAME_DELAY)
        frame=capture_and_process()
        if frame is None:
            pass
        else:
            #frame = Image.fromarray(frame.astype("uint8"))
            rawBytes = frame
            #frame.save(rawBytes, "JPEG")
            frame_base64 = base64.b64encode(frame)
            
            await channel_layer.group_send(
                room_group_name,
                {
                    'type': 'frame_message',
                    'message': frame_base64.decode('utf-8')
                }
            )


class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global NCLIENTS, broadcast_task
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'room_%s' % self.room_name
        NCLIENTS+=1

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        # if no client connected yet, start broadcast task
        if NCLIENTS==1:
            broadcast_task=asyncio.create_task(broadcast_task(self.channel_layer, self.room_group_name))

    async def disconnect(self, close_code):
        global NCLIENTS, broadcast_task
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        NCLIENTS-=1
        if NCLIENTS==0:
            print('*********Stop broadcasting..')
            broadcast_task.cancel()
        
    # Receive message from WebSocket
    async def receive(self, text_data):
        
        pass

    # Receive message from room group
    async def frame_message(self, event):
        # Send message to WebSocket
        msg=event['message']
        print(msg)
        await self.send(text_data=json.dumps({
            'type': 'frame',
            'data': msg
        }))