import cv2 as cv
import mediapipe as mp
import time
import math

class handDetector():
    def __init__(self,mode = False,maxHands = 2, detectionCon = 0.5,trackCon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode= self.mode,
                                        max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence= self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self,img,draw = True):
        imgRGB = cv.cvtColor(img,cv.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLM in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img,handLM,self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self,img, handNo =0):
        lmList = []
        if self.results.multi_hand_landmarks:
            if handNo < len(self.results.multi_hand_landmarks):
                myHand = self.results.multi_hand_landmarks[handNo]
                for id, lm in enumerate(myHand.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id,cx,cy])
        return lmList

    def distance(self,point1,point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)

    def getFingers(self,img,handNo = 0):
        """
        Improved finger detection logic
        Returns list of 0s and 1s for each finger (0=down, 1=up)
        Order: [Thumb, Index, Middle, Ring, Pinky]
        """
        fingers = []
        lmList = self.findPosition(img,handNo= handNo)
        
        # Check if hand landmarks are available
        if len(lmList) == 0:
            return None
            
        # Finger tip and PIP landmark IDs
        tipIds = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
        pipIds = [3, 6, 10, 14, 18]  # PIP joints for comparison
        
        try:
            # Thumb - Special case (compare x-coordinate)
            if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:  # Thumb tip vs thumb IP joint
                fingers.append(1)
            else:
                fingers.append(0)
            
            # Other 4 fingers - Compare y-coordinates (tip vs PIP)
            for i in range(1, 5):
                if lmList[tipIds[i]][2] < lmList[pipIds[i]][2]:  # Tip above PIP joint
                    fingers.append(1)
                else:
                    fingers.append(0)
                    
        except IndexError:
            return None
            
        return fingers


def main():
    pTime = 0
    cap = cv.VideoCapture(0)
    detector = handDetector()
    
    print("Hand Tracking Started. Press 'ESC' to exit.")
    print("Show your hand to the camera to see finger detection.")
    
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read from camera")
            break
            
        img = detector.findHands(img)
        fingers = detector.getFingers(img)
        
        if fingers is not None:
            print(f"Fingers: {fingers} (Thumb, Index, Middle, Ring, Pinky)")
            # Display finger count on screen
            fingerCount = fingers.count(1)
            cv.putText(img, f'Fingers: {fingerCount}', (10, 120), 
                      cv.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)
        else:
            cv.putText(img, 'No hand detected', (10, 120), 
                      cv.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3)
        
        # Calculate and display FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv.putText(img, f'FPS: {int(fps)}', (10, 70), cv.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)
        cv.imshow('Hand Tracking', img)
        
        # Exit on ESC key
        k = cv.waitKey(1) & 0xFF
        if k == 27:  # ESC key
            break

    cap.release()
    cv.destroyAllWindows()
    print("Hand tracking stopped.")


if __name__ == "__main__":
    main()