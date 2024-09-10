# webshooting_detector.py
# Author: Ali Berk Karaarslan
# Date:   11.09.2024
# About:  Uses computer vision techniques to detect Spider-Man's iconic web-shooting gesture. 

# Required Libraries
import mediapipe as mp
import simpleaudio as sa
import random
import math
import time
import cv2

#Calculates The Euclidean Distance Of Given 2 Points.
def calculateEuclideanDistance(point1, point2):
    distance = 0.0
    for i in range(len(point1)):
        distance += (point2[i] - point1[i]) ** 2
    return math.sqrt(distance)


# Finds where a line (from start to end) intersects the screen boundaries and returns the closest intersection point to end.
def findBoundryIntersection(start, end, width, height):    
    
    # Converts normalized start and end points to screen coordinates.
    x1 = int(start[0] * width)
    y1 = int(start[1] * height)
    x2 = int(end[0] * width)
    y2 = int(end[1] * height)
    
    # Handles vertical and horizontal lines separately
    if x1 == x2:
        # Vertical line: return intersection with top or bottom boundary
        if y2 <= y1:
            return (x1, 0)
        else:
            return (x1, height)
        
    # Horizontal Line
    if y1 == y2:
        # Vertical line: return intersection with top or bottom boundary
        if x2 <= x1:
            return (0, x1)
        else:
            return (width, x1)

    # Calculate slope of the line    
    m = (y2 - y1) / (x2 - x1)

    # Finds intersection points
    intersection1 = [findX(m, 0, x1, y1), 0]   # Intersection with top boundary 
    intersection2 = [width, findY(m, width, x1, y1)]   # Intersection with right boundary
    intersection3 = [0, findY(m, 0, x1, y1)]   # Intersection with left boundary
    intersection4 = [findX(m, height, x1, y1), height]   # Intersection with bottom boundary
    
    # Collect valid intersections within screen bounds.
    intersections = []

    if intersection1[0] >= 0 and intersection1[0] <= width:
        intersections.append(intersection1)
    if intersection2[1] >= 0 and intersection2[1] <= height:
        intersections.append(intersection2)
    if intersection3[1] >= 0 and intersection3[1] <= height:
        intersections.append(intersection3)
    if intersection4[0] >= 0 and intersection4[0] <= width:
        intersections.append(intersection4)

    # Determine which intersection is closer to the end point.
    inter1distToStart = calculateEuclideanDistance((x1,y1), intersections[0])
    inter1distToEnd = calculateEuclideanDistance((x2,y2), intersections[0])

    if inter1distToStart < inter1distToEnd : 
        return intersections[1][0], intersections[1][1]
    else:
        return intersections[0][0], intersections[0][1]


# Auxilary Functions For findBoundryIntersection Function.
# Finds The y coordinate of given x coordinate and slope m 
def findY(m, x ,x1, y1):
    return (m * (x - x1)) + y1

# Finds The x coordinate of given y coordinate and slope m 
def findX(m, y ,x1, y1):
    return ((y - y1)/m) + x1


# Imports Web-Shooting Sounds And Returns The Sound Objects As List. Takes Parameters As File Name.
def importWebShooterSounds(*sounds):
    websounds = []
    for s in sounds:
        websounds.append(sa.WaveObject.from_wave_file(s))
    
    return websounds

# Checks If The Given Hand Joint Landmarks Satisfies Predefined Threshold Values.
def checkConditions(world_landmarks):
    point0 = (world_landmarks[0].x, world_landmarks[0].y, world_landmarks[0].z)
    point4 = (world_landmarks[4].x, world_landmarks[4].y, world_landmarks[4].z)
    point8 = (world_landmarks[8].x, world_landmarks[8].y, world_landmarks[8].z)
    point12 = (world_landmarks[12].x, world_landmarks[12].y, world_landmarks[12].z)
    point16 = (world_landmarks[16].x, world_landmarks[16].y, world_landmarks[16].z)
    point20 = (world_landmarks[20].x, world_landmarks[20].y, world_landmarks[20].z)
    
    return (10 <= calculateEuclideanDistance(point16, point12) * 1000 <= 35 and
            60 <= calculateEuclideanDistance(point16, point0) * 1000 <= 120 and
            60 <= calculateEuclideanDistance(point12, point0) * 1000 <= 120 and
            120 <= calculateEuclideanDistance(point20, point0) * 1000 <= 160 and
            115 <= calculateEuclideanDistance(point8, point0) * 1000 <= 190 and
            105 <= calculateEuclideanDistance(point4, point0) * 1000 <= 160)


if __name__ == "__main__":

    #Importing Web Shooter Sounds.
    webshooterSounds = importWebShooterSounds('sounds/snd_web1.wav', 'sounds/snd_web2.wav', 'sounds/snd_web3.wav')

    # Initializing Hand Detection Model.
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    hand = mp_hands.Hands()

    # Opening Cam.
    cap = cv2.VideoCapture(0)
    
    # Initializing Neccessary Variables. For Each Hand, Add One More Element To Lists. Currently, It Can Detect 2 Hands.
    detected = [False, False]
    oldTime = [time.time(), time.time()]

    # Works Until Cam Closed.
    while cap.isOpened():
        success, frame = cap.read()
        height, width, _ = frame.shape

        if success:
            RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hand.process(RGB_frame)

            # If Hand Detected
            if result.multi_hand_landmarks:
                
                # Checks All The Detected Hands.
                for i in range(len(result.multi_hand_landmarks)):

                    hand_landmarks = result.multi_hand_landmarks[i].landmark   # Coordinates That Are Relative To Screen.
                    world_landmarks = result.multi_hand_world_landmarks[i].landmark   # Coordinates That Are Relative To Hand Joints.

                    # Screen Coordinate Of Wrist.
                    point0ScreenCoords = (hand_landmarks[0].x, hand_landmarks[0].y, world_landmarks[0].z)
                    
                    # Screen Coordinate Of Middle Point Of Ring And Middle Finger.
                    handMiddlePointScreenCoords = ((hand_landmarks[14].x + hand_landmarks[10].x )/2, (hand_landmarks[14].y + hand_landmarks[10].y)/2, (hand_landmarks[14].z + hand_landmarks[10].z )/2)
                    
                    # True If Face Palm Is Facing Screen, False Otherwise.
                    palmFacingScreen = world_landmarks[9].z - world_landmarks[11].z > 0
                    
                    try:

                        # Web Shooting Gesture Detected.
                        if checkConditions(world_landmarks):                    
                            coords = findBoundryIntersection(point0ScreenCoords, handMiddlePointScreenCoords, width, height)

                            if palmFacingScreen:
                                # Draws Line Starting From Wrist And Passes The Calculated Middle Point Of Hand.
                                cv2.line(frame, (int(point0ScreenCoords[0] * width), int(point0ScreenCoords[1]* height)), (int(coords[0]),int(coords[1])), color = (245,245,245), thickness=4)
                            else:
                                # Draws Line Starting From The Calculated Middle Point Of Hand.
                                cv2.line(frame, (int(handMiddlePointScreenCoords[0] * width), int(handMiddlePointScreenCoords[1]* height)), (int(coords[0]),int(coords[1])), color = (255,255,255), thickness=4)
                            
                            # Check If The Last Detection Was At Least 7 ms Ago.
                            if (detected[i] == False) and ((time.time() - oldTime[i]) * 1000 > 700) :
                                random.choice(webshooterSounds).play()
                                oldTime[i] = time.time()

                            detected[i] = True

                            # Draw The Landmarks
                            # mp_drawing.draw_landmarks(frame, result.multi_hand_landmarks[i], mp_hands.HAND_CONNECTIONS)                     
                        else:
                            detected[i] = False
                    except Exception as e:
                        pass
        
        # Shows The Camera.
        cv2.imshow("Web Shooter Detector By Ali Berk Karaarslan. Press 'Q' to exit...", frame)
        key = cv2.waitKey(1)
        if key == ord("q"):
            break
    
    # Exit The Program            
    cv2.destroyAllWindows()
    cap.release()