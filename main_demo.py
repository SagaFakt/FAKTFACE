import os
from subprocess import call
from flask import Flask, render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

def open_py_file():
    call(["python","nahichalraha.py"])




app = Flask(__name__)
app.secret_key = "Secret Key"
engine = create_engine('mysql://root:''@127.0.0.1/fakt')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@127.0.0.1/fakt'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Table Creation for login
class Login(db.Model):
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(20), nullable=False)
    #c_password = db.Column(db.String(20), nullable=False)
    organization = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)

# Login Route    
@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    #return "Hello World!"
    if(request.method=='POST'):
        '''Add entry to the database'''
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        organization = request.form.get('organization')
        department = request.form.get('department')
        if(password != None or email != None ):
            entry = Login(username=username, email = email, password = password ,organization = organization,department=department )
            db.session.add(entry)
            db.session.commit()
            redirect('/register')
    return render_template('login.html')

@app.route("/signin")
def signin():
    return render_template("tracksheet_index.html")

# Register_successful Route
@app.route("/register", methods = ['GET', 'POST'])
def register():
    return render_template("register_index.html")

# Tracksheet Route
@app.route("/tracksheet")
def tracksheet():
    return render_template("tracksheet_index.html")

#Table Creation for addVisitor
class AddVisitor(db.Model):
    id=db.Column(db.Integer , primary_key = True)
    vname = db.Column(db.String(50))
    vemail = db.Column(db.String(50))
    vcontact = db.Column(db.Integer, nullable=False)
    vabout = db.Column(db.String(100))

# AddVisitor Route    
@app.route("/addVisitor", methods = ['GET', 'POST'])
def addVisitor():
    if(request.method=='POST'):
        '''Add entry to the database'''
        vname = request.form.get('vname')
        vemail = request.form.get('vemail')
        vcontact = request.form.get('vcontact')
        vabout = request.form.get('vabout')
        if(vcontact != None or vemail != None ):
            entry = AddVisitor(vname=vname, vemail = vemail, vcontact = vcontact ,vabout = vabout )
            db.session.add(entry)
            db.session.commit()
    return render_template('visitor_index.html')

app.run(debug=True)
