import cv2 as cv
import cv2
import os
import numpy as np
from matplotlib import pyplot as plt
from mtcnn import MTCNN
import dlib
import face_recognition
from mtcnn.mtcnn import MTCNN
from keras_facenet import FaceNet
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from django.contrib import messages
import pickle
import requests

def fn_getpics(username,request):
    # Load HAAR face classifier
    face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Load functions
    def face_extractor(img):
        # Function detects faces and returns the cropped face
        # If no face detected, it returns the input image
        
        #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(img, 1.3, 5)
        
        if faces is ():
            return None
        
        # Crop all faces found
        for (x,y,w,h) in faces:
            x=x-10
            y=y-10
            cropped_face = img[y:y+h+50, x:x+w+50]
        return cropped_face

    # Initialize Webcam
    cap = cv2.VideoCapture(0)
    count = 0

    # Create a folder dynamically with a name of your choice
    folder_name = username  # Change this to the desired folder name
    output_directory = os.path.join('training/', folder_name)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Collect 100 samples of your face from webcam input
    while True:
        ret, frame = cap.read()
        if face_extractor(frame) is not None:
            count += 1
            face = cv2.resize(face_extractor(frame), (400, 400))
            #face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            # Save file in specified directory with unique name
            file_name_path = os.path.join(output_directory, 'image_' + str(count) + '.jpg')
            cv2.imwrite(file_name_path, face)

            # Put count on images and display live count
            cv2.putText(face, str(count), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
            cv2.imshow('Face Cropper', face)
            
        else:
            print("Face not found")
            pass

        if (cv.waitKey(1) & 0xFF == 27) or count == 100: #13 is the Enter Key\
            break
            
    cap.release()
    cv2.destroyAllWindows()      
    print("Collecting Samples Complete")
    messages.success(request, "Registered successfully. Training.....")
    return(1)

