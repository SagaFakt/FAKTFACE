import cv2
import os
cam = cv2.VideoCapture(0)
cam.set(3, 640) 
cam.set(4, 480) 
# haarcascade file  on static
face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# unique Id from database
visitor_face_id ='1'

print("\n [INFO] Initializing face capture. Look the camera and wait ...")
count = 0

while(True):

    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)
    
    for (x,y,w,h) in faces:
        
        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
        count += 1

        # Save the captured image into the static folder folder
        cv2.imwrite("dataset/user" + str(visitor_face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
    cv2.imshow('image', img)
    
        

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
    elif count >= 30: 
         break

print("\n Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()


