import cv2
import numpy as np
import time
import autopy
import cvzone.HandTrackingModule as htm

######################
wCam, hCam = 640, 480
frameR = 100     #Frame Reduction
smoothening = 10  #random value
######################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

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
    elif ar == [1, 1, 0, 0, 0]:
        return 6
    elif ar == [1, 1, 1, 0, 0]:
        return 7
    elif ar == [1, 1, 1, 1, 0]:
        return 8
    elif ar == [0, 1, 0, 0, 1]:
        return 9
    elif ar == [1, 1, 0, 0, 1]:
        return 10

detector = htm.HandDetector(maxHands=1)
wScr, hScr = autopy.screen.size()


while True:
    success, img = cap.read()
    hands,img = detector.findHands(img)
    if hands:
        hand = hands[0]
        lmList = hand['lmList']
        handType1 = hand['type']
        h1f = detector.fingersUp(hand)
        h1c = getCount(h1f)
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                          (255, 0, 255), 2)

        #Moving Mode
        if h1c==1:
            #Convert the coordinates
            x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))
            print(x3,y3)
            #Smooth Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            print(clocX,clocY)
            # Step7: Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        #Clicking Mode
        if h1c==2:
            length, img = detector.findDistance(8, 12)
            if length < 80:
                autopy.mouse.click()

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (28, 58), cv2.FONT_HERSHEY_PLAIN, 3, (255, 8, 8), 3)
    cv2.imshow("Image", img)
    cv2.waitKey(1)