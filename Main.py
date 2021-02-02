# Importing the libraries
import cv2
import numpy as np
from pynput.mouse import Button, Controller
import wx

# Making the mouse object
mouse=Controller()

# Initializing the app to get display co-ordinates only
app = wx.App(False)

# Setting the display monitor co-ordinates
(sx, sy) = wx.GetDisplaySize()

# Setting the camera resolution
(camx, camy) = (320, 240)

# Setting the HSV color bounds for detecting green color objects
lowerBound = np.array([33, 80, 40])
upperBound = np.array([102, 255, 255])

# Setting the camera
cam = cv2.VideoCapture(0)

# Setting the camera width and height
cam.set(3, camx) # 3 is the flag for width
cam.set(4, camy) # 4 is the flag for height

# Setting the morphology kernel
kernelOpen = np.ones((5, 5)) # morphology opening kernel
kernelClose = np.ones((20, 20)) # morphology closing kernel

# Setting up hyper-parameters
pinchFlag = 0
openx, openy, openw, openh = 0, 0, 0, 0
mLocOld = np.array([0, 0])
mouseLoc = np.array([0, 0])
Dampingfactor = 4 # used to make the mouse movement less violent

# Main Loop
while True:
    ret, img = cam.read()
    
    # Resizing the image
    img = cv2.resize(img, (320, 240))
    
    # Converting the image to HSV
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Generating mask
    mask = cv2.inRange(imgHSV, lowerBound, upperBound)
    
    # Opening masking to reduce noise in the mask
    maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
    
    # Closing masking to fill gaps in the mask
    maskClose = cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)

    # Setting the final mask to closed mask
    maskFinal = maskClose

    # Getting the contours and hierachy
    conts, h = cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    if len(conts) == 2:
        # If there are two contours present in the image
        
        if pinchFlag == 1: # Flag used to reduce multiple clicks
            pinchFlag = 0
            mouse.release(Button.left)

        # Getting the bounding co-ordinates for both the contours
        x1, y1, w1, h1 = cv2.boundingRect(conts[0])
        x2, y2, w2, h2 = cv2.boundingRect(conts[1])

        # Drawing Bounding Rectangles for both the contours
        cv2.rectangle(img, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), 2)
        cv2.rectangle(img, (x2, y2), (x2 + w2, y2 + h2), (255, 0, 0), 2)

        # Getting the center-points of the bounding rectangles
        cx1 = x1+w1/2
        cy1 = y1+h1/2
        cx2 = x2+w2/2
        cy2 = y2+h2/2

        # Getting the center point of the line joining the midpoints of the rectangles
        cx = (cx1 + cx2)/2
        cy = (cy1 + cy2)/2

        # Drawing the line joining the centers
        cv2.line(img, (int(cx1), int(cy1)), (int(cx2), int(cy2)), (255, 0, 0), 2)
        
        # Drawing a circle around the objects
        cv2.circle(img, (int(cx) ,int(cy)), 2, (0, 0, 255), 2)

        # Setting the mouse position
        mouseLoc = mLocOld + ((cx,cy)-mLocOld)/Dampingfactor # Using the damping factor to smoothen the mouse movement
        mouse.position = (sx-(mouseLoc[0]*sx/camx), mouseLoc[1]*sy/camy)
        mLocOld = mouseLoc

        # Drawing rectange around the entire detected set of objects
        openx, openy, openw, openh=cv2.boundingRect(np.array([[[x1,y1],[x1+w1,y1+h1],[x2,y2],[x2+w2,y2+h2]]])) 
        cv2.rectangle(img,(openx,openy),(openx+openw,openy+openh),(255,0,0),2)

    elif len(conts) == 1:
        # If there is one contour present
        x, y, w, h = cv2.boundingRect(conts[0])

        if pinchFlag == 0:
            if abs(w*h - openw*openh)*100/(h*w) < 20:
                # To detect the case when one of the mouse object goes out of bounds
                pinchFlag=1
                mouse.press(Button.left)
                openx,openy,openw,openh=(0,0,0,0)
        else:
            # To move the mouse only in close gesture
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

            # Getting the center point
            cx = x+w/2
            cy = y+h/2

            # Drawing the circle
            cv2.circle(img,(int(cx),int(cy)),int((w+h)/4),(0,0,255),2)

            # Setting the mouse position
            mouse.position=(sx-(cx*sx/camx), cy*sy/camy)
            mouseLoc=mLocOld+((cx,cy)-mLocOld)/Dampingfactor
            mouse.position=(sx-(mouseLoc[0]*sx/camx), mouseLoc[1]*sy/camy)
            mLocOld=mouseLoc