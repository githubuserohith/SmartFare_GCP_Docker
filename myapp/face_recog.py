import cv2 as cv
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


def save_model_to_drive(model):
    with open('trained_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    # print("Model saved successfully.")


def fn_facetrain():     
    class FACELOADING:
        def __init__(self, directory):
            self.directory = directory
            self.target_size = (160, 160)
            self.X = []
            self.Y = []
            self.detector = MTCNN()

        def extract_face(self, filename):
            img = cv.imread(filename)
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            x, y, w, h = self.detector.detect_faces(img)[0]['box']
            x, y = abs(x), abs(y)
            face = img[y:y+h, x:x+w]
            face_arr = cv.resize(face, self.target_size)
            return face_arr

        def load_faces(self, dir):
            FACES = []
            for im_name in os.listdir(dir):
                try:
                    path = os.path.join(dir, im_name)
                    single_face = self.extract_face(path)
                    FACES.append(single_face)
                except Exception as e:
                    pass
            return FACES

        def load_classes(self):
            for sub_dir in os.listdir(self.directory):
                path = os.path.join(self.directory, sub_dir)
                FACES = self.load_faces(path)
                labels = [sub_dir for _ in range(len(FACES))]
                # print(f"Loaded successfully: {len(labels)}")
                self.X.extend(FACES)
                self.Y.extend(labels)

            return np.array(self.X), np.array(self.Y)

        def plot_images(self):
            pass
            # plt.figure(figsize=(18,16))
            for num, image in enumerate(self.X):
                ncols = 3
                nrows = len(self.Y) // ncols+1
            #     plt.subplot(nrows, ncols, num + 1)
            #     plt.imshow(image)
            #     plt.axis('off')
            # plt.show()

    faceloading=FACELOADING('training/')
    X,Y=faceloading.load_classes()
    # plt.figure(figsize=(30,25))
    for num, image in enumerate(X):
        ncols = 3
        nrows = len(Y) // ncols+1
        # plt.subplot(nrows, ncols, num + 1)
        # plt.imshow(image)
        # plt.axis('off')

    # Detecting
    # os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
    # img=cv.imread(img_name)
    # #opencv BGR channel format and plt read images as RGB channel format
    # img=cv.cvtColor(img,cv.COLOR_BGR2RGB)
    # plt.imshow(img) #RGB-REAL IMAGE
    # detector=MTCNN()
    
    # results=detector.detect_faces(img)
    # print(results) # we only need box
    # #definning boundary box
    # x,y,w,h=results[0]['box']
    # img=cv.rectangle(img,(x,y),(x+w,y+h),(0,0,255),5)
    # plt.imshow(img)
    # my_face=img[y:y+h,x:x+w]
    # #Fcaenet takes as input 160*160 so we will resize it
    # my_face=cv.resize(my_face,(160,160))
    # plt.imshow(my_face)

    # Embedding
    embedder=FaceNet()
    def get_embedding(face_img):
        face_img=face_img.astype('float32')#3d(160*160*3)
        face_img=np.expand_dims(face_img,axis=0)
        #4d (none*160*160*3)
        yhat=embedder.embeddings(face_img)
        return yhat[0]#512D image (1*1*512)
    EMBEDDED_X=[]

    for img in X:
        EMBEDDED_X.append(get_embedding(img))

    EMBEDDED_X=np.asarray(EMBEDDED_X)

    np.savez_compressed('faces_embedding_done_6classes.npz',EMBEDDED_X,Y)

    encoder=LabelEncoder()
    encoder.fit(Y)
    Y=encoder.transform(Y)
    # print(Y)

    X_train ,X_test,Y_train,Y_test=train_test_split(EMBEDDED_X,Y,shuffle=True,random_state=17)

    # SVM model
    model=SVC(kernel='linear',probability=True)
    model.fit(X_train,Y_train)
    ypreds_train=model.predict(X_train)
    ypreds_test=model.predict(X_test)

    # print(accuracy_score(Y_train,ypreds_train))
    # print(accuracy_score(Y_test,ypreds_test))

    # Call the function to save the model
    save_model_to_drive(model)

    # return (X,Y,1)


def fn_facepred():
    facenet=FaceNet()
    faces_embeddings=np.load("faces_embedding_done_6classes.npz")
    Y=faces_embeddings['arr_1']
    encoder=LabelEncoder()
    encoder.fit(Y)
    haarcascade=cv.CascadeClassifier("haarcascade_frontalface_default.xml")
    model=pickle.load(open("trained_model.pkl",'rb'))
    name = []
    cap = cv.VideoCapture(0)  # Accessing webcam (assuming it's the first camera)
    while cap.isOpened():
        _, frame = cap.read()
        rgb_img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        gray_img = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = haarcascade.detectMultiScale(gray_img, 1.3, 5)
        for x,y,w,h in faces:
            img = rgb_img[y:y+h, x:x+w]
            img = cv.resize(img, (160,160)) # 1x160x160x3
            img = np.expand_dims(img,axis=0)
            ypred = facenet.embeddings(img)
            face_name = model.predict(ypred)
            final_name = encoder.inverse_transform(face_name)[0]
            cv.rectangle(frame, (x,y), (x+w,y+h), (255,0,255), 10)
            cv.putText(frame, str(final_name), (x,y-10), cv.FONT_HERSHEY_SIMPLEX,
                    1, (0,0,255), 3, cv.LINE_AA)
            name.append(final_name)

        cv.imshow("Face Recognition:", frame)
        if cv.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv.destroyAllWindows()
    return(list(set(name)))
    
    # cap.release()
    # cv.destroyAllWindows

    # Prediction
    # t_im=cv.imread(img_name)
    # t_im=cv.cvtColor(t_im,cv.COLOR_BGR2RGB)
    # x,y,w,h=MTCNN().detect_faces(t_im)[0]['box']
    # t_im=t_im[y:y+h,x:x+w]
    # t_im=cv.resize(t_im,(160,160))
    # test_im=get_embedding(t_im)

    # test_im=[test_im]
    # test_im=cv.resize(t_im,(160,160))
    # test_im=get_embedding(t_im)
    # test_im=[test_im]

    # ypreds=model.predict(test_im)
    # ypreds
    # encoder.inverse_transform(ypreds)
    # print(encoder.inverse_transform(ypreds))

    # return (encoder.inverse_transform(ypreds)[0], model)
    


