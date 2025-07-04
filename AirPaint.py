import cv2
import numpy as np
import time
import HandTrackingModule as htm
import math

# Canvas settings
wCam, hCam = 1280, 720
brushThickness = 15
eraserThickness = 50

# Color palette
colors = [(255, 0, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255)]
colorNames = ["Magenta", "Red", "Green", "Blue", "Yellow", "Cyan"]
drawColor = (255, 0, 255)  # Default magenta

# Initialize
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon=0.75, maxHands=1)
imgCanvas = np.zeros((hCam, wCam, 3), np.uint8)

class AirPaint:
    def __init__(self):
        self.mode = "drawing"
        self.colorIndex = 0
        self.thickness = brushThickness
        self.lastColorChange = 0
        self.lastThicknessChange = 0
        self.lastModeChange = 0
        self.smoothing_factor = 0.7  # For smooth drawing
        self.xp, self.yp = 0, 0  # Previous finger positions
        
    def draw_header(self, img):
        """Draw the header with color palette and current settings"""
        # Draw color palette
        for i, color in enumerate(colors):
            cv2.rectangle(img, (50 + i * 100, 0), (150 + i * 100, 80), color, -1)
            cv2.rectangle(img, (50 + i * 100, 0), (150 + i * 100, 80), (0, 0, 0), 2)
            
        # Highlight current color
        cv2.rectangle(img, (50 + self.colorIndex * 100, 0), (150 + self.colorIndex * 100, 80), (255, 255, 255), 5)
        
        # Draw eraser button
        cv2.rectangle(img, (700, 0), (800, 80), (0, 0, 0), -1)
        cv2.putText(img, "ERASE", (710, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Draw clear button
        cv2.rectangle(img, (850, 0), (950, 80), (100, 100, 100), -1)
        cv2.putText(img, "CLEAR", (860, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Show current settings
        cv2.putText(img, f"Mode: {self.mode.title()}", (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, f"Thickness: {self.thickness}", (250, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, f"Color: {colorNames[self.colorIndex]}", (450, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
    def get_gesture_action(self, fingers, lmList):
        """Determine action based on finger gestures"""
        current_time = time.time()
        
        if len(lmList) == 0:
            return "none"
            
        # Only index finger up - Drawing mode
        if fingers == [0, 1, 0, 0, 0]:
            return "drawing"
        
        # Index and middle finger up - Selection mode (no drawing)
        elif fingers == [0, 1, 1, 0, 0]:
            return "selection"
        
        # Thumb and index up - Thickness control
        elif fingers == [1, 1, 0, 0, 0]:
            if current_time - self.lastThicknessChange > 0.5:  # Debounce
                return "thickness"
            return "selection"
        
        # All fingers up - Clear canvas
        elif fingers == [1, 1, 1, 1, 1]:
            if current_time - self.lastModeChange > 1.0:  # Prevent accidental clearing
                return "clear"
            return "selection"
        
        # Three fingers up (index, middle, ring) - Color change
        elif fingers == [0, 1, 1, 1, 0]:
            if current_time - self.lastColorChange > 0.8:  # Debounce
                return "color_change"
            return "selection"
        
        # Pinky up with index - Eraser mode
        elif fingers == [0, 1, 0, 0, 1]:
            return "eraser"
        
        return "selection"
    
    def handle_thickness_control(self, lmList):
        """Control brush thickness using thumb and index finger distance"""
        if len(lmList) >= 9:
            x1, y1 = lmList[4][1], lmList[4][2]  # Thumb tip
            x2, y2 = lmList[8][1], lmList[8][2]  # Index finger tip
            
            length = math.hypot(x2 - x1, y2 - y1)
            # Map distance to thickness (20-150 pixels distance -> 5-50 thickness)
            self.thickness = int(np.interp(length, [20, 150], [5, 50]))
            self.lastThicknessChange = time.time()
            
            return x1, y1, x2, y2, length
        return None
    
    def handle_color_selection(self, lmList, img):
        """Handle color selection when in header area"""
        if len(lmList) >= 9:
            x, y = lmList[8][1], lmList[8][2]  # Index finger tip
            
            # Check if finger is in header area
            if y < 80:
                # Check color palette
                for i in range(len(colors)):
                    if 50 + i * 100 < x < 150 + i * 100:
                        self.colorIndex = i
                        self.lastColorChange = time.time()
                        return True
                
                # Check eraser button
                if 700 < x < 800:
                    self.mode = "eraser"
                    self.lastModeChange = time.time()
                    return True
                
                # Check clear button
                if 850 < x < 950:
                    return "clear"
                    
        return False

def main():
    global imgCanvas
    air_paint = AirPaint()
    pTime = 0
    
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)  # Flip for mirror effect
        
        # Find hands
        img = detector.findHands(img, draw=False)
        lmList = detector.findPosition(img)
        
        if len(lmList) != 0:
            # Get finger positions
            try:
                fingers = detector.getFingers(img)
                
                # Get current action based on gestures
                action = air_paint.get_gesture_action(fingers, lmList)
                
                # Handle different actions
                if action == "drawing":
                    air_paint.mode = "drawing"
                    x1, y1 = lmList[8][1], lmList[8][2]  # Index finger tip
                    
                    # Smooth drawing
                    if air_paint.xp == 0 and air_paint.yp == 0:
                        air_paint.xp, air_paint.yp = x1, y1
                    
                    # Apply smoothing
                    smooth_x = int(air_paint.smoothing_factor * air_paint.xp + (1 - air_paint.smoothing_factor) * x1)
                    smooth_y = int(air_paint.smoothing_factor * air_paint.yp + (1 - air_paint.smoothing_factor) * y1)
                    
                    # Draw on canvas (only if not in header area)
                    if y1 > 120:
                        cv2.line(img, (air_paint.xp, air_paint.yp), (smooth_x, smooth_y), colors[air_paint.colorIndex], air_paint.thickness)
                        cv2.line(imgCanvas, (air_paint.xp, air_paint.yp), (smooth_x, smooth_y), colors[air_paint.colorIndex], air_paint.thickness)
                    
                    air_paint.xp, air_paint.yp = smooth_x, smooth_y
                    
                    # Draw finger indicator
                    cv2.circle(img, (x1, y1), 15, colors[air_paint.colorIndex], cv2.FILLED)
                
                elif action == "eraser":
                    air_paint.mode = "eraser"
                    x1, y1 = lmList[8][1], lmList[8][2]  # Index finger tip
                    
                    if air_paint.xp == 0 and air_paint.yp == 0:
                        air_paint.xp, air_paint.yp = x1, y1
                    
                    # Erase on canvas (only if not in header area)
                    if y1 > 120:
                        cv2.line(img, (air_paint.xp, air_paint.yp), (x1, y1), (0, 0, 0), eraserThickness)
                        cv2.line(imgCanvas, (air_paint.xp, air_paint.yp), (x1, y1), (0, 0, 0), eraserThickness)
                    
                    air_paint.xp, air_paint.yp = x1, y1
                    
                    # Draw eraser indicator
                    cv2.circle(img, (x1, y1), eraserThickness//2, (0, 0, 0), 2)
                
                elif action == "thickness":
                    air_paint.mode = "thickness_control"
                    thickness_data = air_paint.handle_thickness_control(lmList)
                    if thickness_data:
                        x1, y1, x2, y2, length = thickness_data
                        # Draw thickness control visualization
                        cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
                        cv2.circle(img, (x1, y1), 10, (255, 255, 255), cv2.FILLED)
                        cv2.circle(img, (x2, y2), 10, (255, 255, 255), cv2.FILLED)
                        cv2.putText(img, f"Thickness: {air_paint.thickness}", (x1-50, y1-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    air_paint.xp, air_paint.yp = 0, 0
                
                elif action == "color_change":
                    air_paint.colorIndex = (air_paint.colorIndex + 1) % len(colors)
                    air_paint.lastColorChange = time.time()
                    air_paint.mode = "color_changed"
                    air_paint.xp, air_paint.yp = 0, 0
                
                elif action == "clear":
                    imgCanvas = np.zeros((hCam, wCam, 3), np.uint8)
                    air_paint.lastModeChange = time.time()
                    air_paint.mode = "cleared"
                    air_paint.xp, air_paint.yp = 0, 0
                
                elif action == "selection":
                    # Check if finger is in header for color selection
                    header_action = air_paint.handle_color_selection(lmList, img)
                    if header_action == "clear":
                        imgCanvas = np.zeros((hCam, wCam, 3), np.uint8)
                        air_paint.mode = "cleared"
                    elif header_action:
                        air_paint.mode = "color_selected"
                    else:
                        air_paint.mode = "selection"
                    air_paint.xp, air_paint.yp = 0, 0
                
                else:
                    air_paint.xp, air_paint.yp = 0, 0
                    
            except Exception as e:
                air_paint.xp, air_paint.yp = 0, 0
        else:
            air_paint.xp, air_paint.yp = 0, 0
        
        # Merge canvas with camera image
        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)
        
        # Draw header
        air_paint.draw_header(img)
        
        # Draw instructions
        instructions = [
            "Gestures:",
            "Index up: Draw",
            "Index+Middle: Select",
            "Thumb+Index: Thickness",
            "Index+Middle+Ring: Color",
            "Index+Pinky: Erase",
            "All fingers: Clear"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(img, instruction, (wCam - 300, 150 + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (10, hCam - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        cv2.imshow("Air Paint", img)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC key
            break
        elif key == ord('c'):  # Clear canvas
            imgCanvas = np.zeros((hCam, wCam, 3), np.uint8)
        elif key == ord('s'):  # Save canvas
            cv2.imwrite(f"air_paint_{int(time.time())}.jpg", imgCanvas)
            print("Canvas saved!")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 