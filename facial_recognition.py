import cv2
import os
import numpy as np
import time

import face_recognition

from screen import turnoff, turnon



#function to detect faces using OpenCV
def detect_faces(img):
	#convert the test image to gray scale as opencv face detector expects gray images
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	 
	#load OpenCV face detector, I am using LBP which is fast
	#there is also a more accurate but slow: Haar classifier
	cascPath = "haarcascade_frontalface_alt2.xml"
	
	face_cascade = cv2.CascadeClassifier(cascPath)

	#let's detect multiscale images(some images may be closer to camera than others)
	#result is a list of faces
	faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5);
	 
	#if no faces are detected then return original img
	if len(faces) == 0:
		return None, None
	 
	#under the assumption that there will be only one face for training images,
	#extract the face area
	elif len(faces) == 1:
		(x, y, w, h) = faces[0]
		return [gray[y:y+w, x:x+h]], faces
	else:
		#return only the face part of the image
		return [gray[y:y+w, x:x+h] for x, y, w, h in faces], faces


def add_face(label, numOfImages):
	# Add new face to face recognition collection
	if not os.path.isdir("training-data/" + label):
		os.makedirs("training-data/" + label)
	cam = cv2.VideoCapture(0)
	for i in range(numOfImages):
		s, img = cam.read()
		cv2.imwrite("training-data/{}/{}{}.jpg".format(label, label, i), img)
		time.sleep(1)

def prepare_training_data(data_folder_path):
	dirs = os.listdir(data_folder_path)

	faces = []
	labels = []

	HEIGHT, WIDTH = cv2.imread(data_folder_path + "/Seth/Seth0.jpg").shape[:2]
	print(HEIGHT, WIDTH)
	for dir_name in dirs:
		label = dir_name
		label_dir_path = data_folder_path + "/" + dir_name

		image_names = os.listdir(label_dir_path)
		for image_name in image_names:
			image_path = label_dir_path + "/" + image_name
			image = cv2.imread(image_path)
			cv2.imshow("Training on image..", image)
			cv2.waitKey(100)
			detected_faces, rect = detect_faces(image)
			if detected_faces is not None:
				for face in detected_faces:
					if face is not None:

						resized_face = cv2.resize(face, (100, 100), interpolation=cv2.INTER_CUBIC)
						faces.append(resized_face)
						if label == "Seth":
							labels.append(1)
						if label == "Sam":
							labels.append(2)
						if label == "Seth Rogen":
							labels.append(3)

	cv2.destroyAllWindows()
	cv2.waitKey(1)
	cv2.destroyAllWindows()
	return faces, labels

def train_save(save_as=None):
	faces, labels = prepare_training_data("training-data")

	print("Total faces: ", len(faces))
	print("Total labels: ", len(labels))

	face_recognizer = cv2.face.LBPHFaceRecognizer_create(threshold=100)
	#face_recognizer = cv2.face.FisherFaceRecognizer_create()
	face_recognizer.train(faces, np.array(labels))
	if save_as is not None:
		#face_recognizer.save('LBPH_recognize_model.yml')
		face_recognizer.save(save_as)

def predict(face_recognizer, subjects, test_img):
	img = test_img

	faces, rects = detect_faces(img)

	if faces is not None and rects is not None:
		for face, rect in zip(faces, rects):
			if face is not None and rect is not None:
				resized_webcam_face = cv2.resize(face, (100, 100), interpolation=cv2.INTER_CUBIC)
				label = face_recognizer.predict(resized_webcam_face)
				print(label)
				label_text = subjects[label[0]] + " - " + str(round(label[1], 1))

				(x, y, w, h) = rect
				cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
				cv2.putText(img, label_text, (x, y - 15), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
		return img, label[0]
	return img, None

