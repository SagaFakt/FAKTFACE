from flask import Flask, render_template,url_for,request,session,logging,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine,update
from sqlalchemy.orm import scoped_session,sessionmaker
from passlib.hash import sha256_crypt
import cv2
import numpy as np
import os
from PIL import Image
import time


id_count = 0 
ids = 0
def trainer():
    
    path = 'static/dataSet'

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier("static/haarcascade_frontalface_default.xml");

    def getImagesAndLabels(path):

        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
        faceSamples=[]
        ids = []

        for imagePath in imagePaths:

            PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
            img_numpy = np.array(PIL_img,'uint8')

            id = int(os.path.split(imagePath)[-1].split(".")[0])
            faces = detector.detectMultiScale(img_numpy)

            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)

        return faceSamples,ids

    print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    faces,ids = getImagesAndLabels(path)
    recognizer.train(faces, np.array(ids))


    #PATH FOR TRAINER.YML
    recognizer.write('static/trainer/trainer.yml')
    print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))



def dataset(id = id):
    import cv2
    import os
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) 
    cam.set(4, 480) 
    # haarcascade file  on static
    face_detector = cv2.CascadeClassifier('static/haarcascade_frontalface_default.xml')

    # unique Id from database
    visitor_face_id =str(id)

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
            cv2.imwrite("static/dataset/" + str(visitor_face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
        cv2.imshow('image', img)
        #time.sleep(0.5)
    
        

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
        elif count >= 30: 
            break

    print("\n Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()
    trainer()


def recognition():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('static/trainer/trainer.yml')   #load trained model    
    cascadePath = "static/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)

    font = cv2.FONT_HERSHEY_SIMPLEX



    name_id = {14321:'Ayushi',36112:'Sudhanshu',95812:'Ashish'}  #key in names, start from the second place, leave first empty

    cam = cv2.VideoCapture(0)
    cam.set(3, 640) 
    cam.set(4, 480) 

    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)
    face_ids = []
    ids = 0   
    while True:

        ret, img =cam.read()

        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
         minNeighbors = 5,
         minSize = (int(minW), int(minH)),
        )

        for(x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

            if (100-confidence < 100 and 100-confidence>20):
                ids = id
                confidence = "  {0}%".format(round(100 - confidence))
            
            else:
                ids = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))
        
            cv2.putText(img, str(ids), (x+5,y-5), font, 1, (255,255,255), 2)
            cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
    
        cv2.imshow('camera',img)
        if ids != 'unknown':
            face_ids.append(ids)
       

        k = cv2.waitKey(10) & 0xff 
        if k == 27:
            break

    face_ids = set(face_ids)
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()
    return face_ids






app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/fakt'
app.config['SECRET_KEY'] = 'secret key'    
db = SQLAlchemy(app)

engine=create_engine("mysql://root:@localhost/fakt")
#mysql+pymysql://username:password@localhost/databasename
dbase=scoped_session(sessionmaker(bind=engine))

#Table Creation for login
class Login(db.Model):
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(256), nullable=False)
    #c_password = db.Column(db.String(20), nullable=False)
    organization = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)

# Login Route    
@app.route("/login", methods = ['POST','GET'])
def signup():
    #signup_form = request.form.get('signup_form')
    #signin_form = request.form.get('signin_form')
    rname= request.form.get('signup_btn')
    lname= request.form.get('signin_btn')
              
    if request.method =="POST" and rname == 'Sign up':
        rusername = request.form.get('rusername')
        remail = request.form.get('remail')
        rpassword = request.form.get('rpassword')
        #c_password = request.form.get('c_password')
        rorganization = request.form.get('rorganization')
        rdepartment = request.form.get('rdepartment')
        secure_password=sha256_crypt.encrypt(str(rpassword))
        #return render_template("test.html",passw = rpassword)
        useremail=dbase.execute("SELECT email FROM login WHERE email=:email",{"email":remail}).fetchone()
        #usernamedata=str(usernamedata)s
        if useremail == None:
            dbase.execute("INSERT INTO login(username,email,password,organization,department) VALUES(:username,:email,:password,:organization,:department)",{"username":rusername,"email":remail,"password":secure_password,"organization":rorganization,"department":rdepartment})
            dbase.commit()
            flash("You are registered and can now login","success")
            return redirect('/register')
        else:
            flash("user already existed, please login or contact admin","danger")
            return redirect("/login")

    

    if request.method == "POST" and lname == 'Sign in':
        lemail=request.form.get("lemail")
        lpassword=request.form.get("lpassword")

        useremaildata=dbase.execute("SELECT email FROM login WHERE email=:email",{"email":lemail}).fetchone()
        passworddata=dbase.execute("SELECT password FROM login WHERE email=:email",{"email":lemail}).fetchone()

        if useremaildata is None:
            flash("No username","danger")
            return 'No user exist'
        else:
            for passwor_data in passworddata:
                if sha256_crypt.verify(lpassword,passwor_data):
                    session=True
                    flash("You are now logged in!!","success")
                    return redirect('/tracksheet') #to be edited from here do redict to either svm or home
                else:
                    flash("incorrect password")
                    
                    #return render_template("test.html")

    return render_template("login.html")

#tracksheet

@app.route("/live")
def live():
    ids = {2}#recognition()#{1,2,5}
    for cap_id in ids:
            vemail=dbase.execute("SELECT vemail FROM addvisitor WHERE ID=:cap_id",{"cap_id":cap_id}).fetchone()
            vname=dbase.execute("SELECT vname FROM addvisitor WHERE ID=:cap_id",{"cap_id":cap_id}).fetchone()
            vabout=dbase.execute("SELECT vabout FROM addvisitor WHERE ID=:cap_id",{"cap_id":cap_id}).fetchone()
            #v=vname[0][0]
            #a=vabout[2][0]
            dbase.execute("INSERT INTO tracksheet(id,tname,tabout) VALUES(:id,:name,:about)",{"id":cap_id,"name":vname[0],"about":vabout[0]})
            dbase.commit()
    return render_template("test.html",name=vname,email=vemail,about=vabout)
            
@app.route("/tracksheet",methods=['GET','POST'])
def tracksheet():
        
        #passworddata=dbase.execute("SELECT password FROM login WHERE email=:email",{"email":lemail}).fetchone()
        return render_template('tracksheet_index.html')       


    

   # for fetch_id in idds:
       # vnamedata=dbase.execute("SELECT vname FROM addvisitor WHERE id=:id",{"id":fetch_id}).fetchone()
       # vaboutdata=dbase.execute("SELECT vabout FROM addvisitor WHERE id=:id",{"id":fetch_id}).fetchone()
    
       

        
        

# Register_successful Route
@app.route("/register", methods = ['GET', 'POST'])
def register():
    return render_template('register_index.html')



#Table Creation for addVisitor

# AddVisitor Route   
@app.route("/image_capture")
def imagec():
    #dbase.execute("INSERT INTO addvisitor(vname,vemail,vcontact,vabout) VALUES(:vname,:vemail,:vcontact,:vabout)",{"vname":'',"vemail":'',"vcontact":'',"vabout":''})
    #dbase.commit()
    #id = dbase.execute("SELECT id FROM addvisitor WHERE id=:email",{"email":''}).fetchone()
          
    dataset(2)
    return 'dfdf'

@app.route("/addVisitor", methods = ['GET', 'POST'])
def addVisitor():
    
    pre_id = dbase.execute("SELECT id FROM addvisitor ").fetchall()
    
 
    #li = pre_id
    id = str(pre_id[-1])
    id = (int(id[-3]))+1
    #id_count = int(pre_id[length_pre_id-1]+1)
    #id_count = id_count+1     
    
    
    #btn = request.form.get("vcapture")
    #return render_template("test.html",name=btn)
    
    if request.method =="POST":
        vname = request.form.get('vname')
        vemail = request.form.get('vemail')
        vcontact = request.form.get('vcontact')
        vabout = request.form.get('vabout')
        #upd = update(addVisitor).values({"vname" : vname,"vemail":vemail,"vcontact":vcontact,"vabout":vabout}).where(id == id)
        #stmt = (update addvisitor where(addvisitor.id == id).values(vname=vname,vemail=vemail,vcontact=vcontact,vabout=vabout))
        #dbase.execute("UPDATE addvisitor SET vname:vname,vemail:vemail,vcontact:vcontact,vabout:vabout WHERE id:id)",{"id":id,"vemail":vemail,"vname":vname,"vcontact":vcontact,"vabout":vabout})
        #return render_template("test.html",name=vname)
        dbase.execute("INSERT INTO addvisitor(id,vname,vemail,vcontact,vabout) VALUES(:id,:vname,:vemail,:vcontact,:vabout)",{"id":id,"vname":vname,"vemail":vemail,"vcontact":vcontact,"vabout":vabout})
        dbase.commit()
        redirect('/addVisitor')    
        #return render_template("test.html",name=vname,id=str(uuid4))
        #return redirect('/addViitor')
    return render_template('visitor_index.html')

app.run(debug=True)




