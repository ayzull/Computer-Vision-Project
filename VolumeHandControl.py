import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam ,  hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.75)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

volRange = volume.GetVolumeRange()
volume.SetMasterVolumeLevel(0, None)
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
# volume.GetMute()

while True:
    success, img = cap.read()
    img = detector.findHands(img, draw=False)
    lmList = detector.findPosition(img)
    if len(lmList) != 0:
        print(lmList[4], lmList[8])  # Print the coordinates of the thumb and index finger tips

        x1, y1 = lmList[4][1], lmList[4][2]  # Thumb tip coordinates
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img,  (x1, y1), 15, (255, 0, 255), cv2.FILLED) 
        cv2.circle(img,  (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1) , (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2-x1, y2-y1)  # Calculate the distance between thumb and index finger tips
        print(length)

        # Hand range 50 - 300
        # Volume range -96 - 0
        vol = np.interp(length, [50, 280], [minVol, maxVol]) #convert length to volume
        print(vol)
        volume.SetMasterVolumeLevel(vol, None) #set volume
        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED) #button press effect
            

    # Draw the volume bar
    volBar = np.interp(vol, [minVol, maxVol], [400, 150])  # Map volume to bar height
    volPer = np.interp(vol, [minVol, maxVol], [0, 100])  # Map volume to percentage
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)  # Draw the volume bar outline
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)  # Fill the volume bar
    cv2.putText(img, f'{int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)  # Display volume percentage


    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)