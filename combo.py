import cv2
import numpy as np
import HTM as htm
import time
import autopy

from cvzone.HandTrackingModule import HandDetector
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

######################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 10  # random value
######################

detector2 = HandDetector(detectionCon=0.9, maxHands=2)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volMin, volMax = volume.GetVolumeRange()[:2]


def getCount(ar):
    if ar == [0, 0, 0, 0, 0]:
        return 0
    elif ar == [0, 1, 0, 0, 0]:
        return 1
    elif ar == [0, 1, 1, 0, 0]:
        return 2
    elif ar == [0, 1, 1, 1, 0]:
        return 3
    elif ar == [0, 1, 1, 1, 1]:
        return 4
    elif ar == [1, 1, 1, 1, 1]:
        return 5
    elif ar == [0, 1, 0, 0, 1]:
        return 6
    elif ar == [0, 1, 0, 1, 1]:
        return 7
    elif ar == [1, 1, 0, 0, 0]:
        return 8


pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=2)
wScr, hScr = autopy.screen.size()

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    hands, img = detector2.findHands(img)
    lmList, bbox = detector.findPosition(img)
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        fingers = detector.fingersUp()
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)
        # Moving Mode
        if fingers[0] == 0 and fingers[3] == 0 and fingers[4] == 0 and fingers[1] == 1 and fingers[2] == 1:
            # Convert the coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            # Smooth Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # Clicking Mode
        if fingers == [1, 1, 1, 0, 0]:
            # distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            if length < 80:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()

    if hands:
        global h1c
        global h2c
        global bri
        global vol
        global vs
        global bs

        if len(hands) == 2:
            hand1 = hands[0]
            lmList1 = hand1["lmList"]
            bbox1 = hand1["bbox"]
            centerPoint1 = hand1["center"]
            handType1 = hand1["type"]
            h1f = detector.fingersUp(hand1)
            h1c = getCount(h1f)
            cv2.putText(img, str(h1c), (10, 40), cv2.FONT_ITALIC, 1, (0, 255, 98), 3)

            hand2 = hands[1]
            lmList2 = hand2["lmList"]
            bbox2 = hand2["bbox"]
            centerPoint2 = hand2["center"]
            handType2 = hand2["type"]
            h2f = detector.fingersUp(hand2)
            h2c = getCount(h2f)
            cv2.putText(img, str(h2c), (400, 40), cv2.FONT_ITALIC, 1, (0, 255, 98), 3)
            print(handType1, handType2)

            listV1 = [-65.25, -33.23651123046875, -23.654823303222656, -17.829605102539062, -10.329694747924805,
                      -7.626824855804443, -5.290315628051758, -3.4243249893188477, -1.6639597415924072, 0, 0]
            listB = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            listB1 = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

            # Volume
            vs = 0
            bs = 8
            if h1c == vs and h2c == vs:
                volume.SetMasterVolumeLevel(-63.5, None)
            if handType1 == "Left" and h1c == vs and h2c != vs:  # Left Host
                fc = h2c
                for i in range(1, 6):
                    if i == fc:
                        vol = listV1[i + 5]
                        print(vol)
                        volume.SetMasterVolumeLevel(vol, None)
            if handType2 == "Left" and h2c == vs and h1c != vs:  # Left Host
                fc = h1c
                for i in range(1, 6):
                    if i == fc:
                        vol = listV1[i + 5]
                        print(vol)
                        volume.SetMasterVolumeLevel(vol, None)
            if handType1 == "Right" and h1c == vs and h2c != vs:  # Right Host
                fc = h2c
                for i in range(1, 6):
                    if i == fc:
                        vol = listV1[i]
                        print(vol)
                        volume.SetMasterVolumeLevel(vol, None)
            if handType2 == "Right" and h2c == vs and h1c != vs:  # Right Host
                fc = h1c
                for i in range(1, 6):
                    if i == fc:
                        vol = listV1[i]
                        print(vol)
                        volume.SetMasterVolumeLevel(vol, None)

            # Brightness
            if h1c == bs and h2c == bs:
                sbc.set_brightness(0)
            if handType1 == "Left" and h1c == bs and h2c != bs:  # Left Host
                fc = h2c
                for i in range(1, 6):
                    if i == fc:
                        bri = listB1[i + 5]
                        print(bri)
                        sbc.set_brightness(bri)

            if handType2 == "Left" and h2c == bs and h1c != bs:  # Left Host
                fc = h1c
                for i in range(1, 6):
                    if i == fc:
                        bri = listB1[i + 5]
                        print(bri)
                        sbc.set_brightness(bri)

            if handType1 == "Right" and h1c == bs and h2c != bs:  # Right Host
                fc = h2c
                for i in range(1, 6):
                    if i == fc:
                        bri = listB1[i]
                        print(bri)
                        sbc.set_brightness(bri)
            if handType2 == "Right" and h2c == bs and h1c != bs:  # Right Host
                fc = h1c
                for i in range(1, 6):
                    if i == fc:
                        bri = listB1[i]
                        print(bri)
                        sbc.set_brightness(bri)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (28, 58), cv2.FONT_HERSHEY_PLAIN, 3, (255, 8, 8), 3)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
