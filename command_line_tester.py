import os 
import cv2
import numpy as np
import glob

from dlib import get_frontal_face_detector
from dlib import shape_predictor
from dlib import rectangle

def ComputeFaceLandMarks(image, ModelName):
    shape = np.zeros((68,2),dtype=int)
    boundingBox = [-1,-1,-1,-1]

    detector = get_frontal_face_detector()
    if os.name is 'posix': #is a mac or linux
        scriptDir = os.path.dirname(sys.argv[0])
    else: #is a  windows 
        scriptDir = os.getcwd()
    if ModelName == 'iBUG':  #user wants to use iBUGS model
        predictor = shape_predictor(scriptDir + os.path.sep + 'include' +os.path.sep +'data'+ os.path.sep + 'shape_predictor_68_face_landmarks.dat')
    elif ModelName == 'MEE':  #user wants to use MEE model
        predictor = shape_predictor(scriptDir + os.path.sep + 'include' +os.path.sep +'data'+ os.path.sep + 'mee_shape_predictor_68_face_landmarks.dat')
    else: #user wants to use own model        
        predictor = shape_predictor(os.path.normpath(ModelName))
        
    height, width, d = image.shape                        
    if d > 1:
        #transform to gray 
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    #resize to speed up face dectection
    #height, width = gray.shape[:2]  
    newWidth=200
    ScalingFactor=width/newWidth
    newHeight=int(height/ScalingFactor)
    smallImage=cv2.resize(gray, (newWidth, newHeight), interpolation=cv2.INTER_AREA)

    #detect face in image using dlib.get_frontal_face_detector()
    rects = detector(smallImage,1)

    if len(rects) == 0 : #if no face detected then try again with the full size image
            rects = detector(gray,1)            

    if len(rects) == 1:   
        #now we have only one face in the image
        #function to obtain facial landmarks using dlib 
        #given an image and a face
        #rectangle
        for (i, rect) in enumerate(rects):
            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy array

            #adjust face position using the scaling factor
            mod_rect=rectangle(
                    left=int(rect.left() * ScalingFactor), 
                    top=int(rect.top() * ScalingFactor), 
                    right=int(rect.right() * ScalingFactor), 
                    bottom=int(rect.bottom() * ScalingFactor))

            #predict facial landmarks 
            shape_dlib = predictor(image, mod_rect)   
            #shape_dlib = predictor(gray, rect) 
            #transform shape object to np.matrix type
            for k in range(0,68):
                shape[k] = (shape_dlib.part(k).x, shape_dlib.part(k).y)
                if shape[k,0]<= 0 : shape[k,0] = 1
                if shape[k,1]<= 0 : shape[k,1] = 1
        
            #position of the face in the image
            boundingBox=[int(rect.left() * ScalingFactor), 
                        int(rect.top() * ScalingFactor),
                        int(rect.right() * ScalingFactor) - int(rect.left() * ScalingFactor),
                        int(rect.bottom() * ScalingFactor) - int(rect.top() * ScalingFactor)]
    return shape, boundingBox

def DrawResults(image, shape, boundingBox):
    for k in range(0, 68):
        cv2.circle(image,(shape[k,0],shape[k,1]), 5, (0,0,255), -1)

#    cv2.rectangle(image, (boundingBox[0],boundingBox[1]), (boundingBox[2],boundingBox[3]), (255, 0 , 0), 2)

if __name__ == "__main__":
    modelName = 'MEE'
    
    scriptDir = os.getcwd()
    out = glob.glob( scriptDir + os.path.sep +"db" + os.path.sep + "*.jpg" ) 
    n = 0
    for f in out:
        print(100*(n/len(out)))
        filenameFull = os.path.basename(f)
        filename, file_extension = os.path.splitext(filenameFull)
        print(filename)
        image = cv2.imread(f)
        shape, boundingBox =  ComputeFaceLandMarks(image, modelName)
        DrawResults(image, shape, boundingBox)
        np.savetxt("db"+os.path.sep+filename+".csv", shape, delimiter=',', fmt='%d')
        cv2.imwrite("db"+os.path.sep+filename+"_out.jpg",image)
        n = n +1