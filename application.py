import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

#api key for goodreads: ysbBSxzUW58cfo5kCo7FNw

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html") #done 
	
@app.route("/signuppage")
def signuppage():
	return render_template("signup.html") #done
	
@app.route("/signin", methods=['POST'])
def signin():
	name = request.form.get("inputUsername")
	password = request.form.get("inputPassword")
	
	# Make sure username exists.
	if db.execute("SELECT * FROM users WHERE username = :username", {"username": name}).rowcount != 1:
		return render_template("invalidSignIn.html", username= name) #done
	
	if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": name, 
	"password": password}).rowcount == 1:
		return render_template("personalPage.html") #do up html page 
	else:
		return render_template("invalidPassword.html", username= name)#done
	
	
@app.route("/signup", methods=['POST'])
def signup():
	name = request.form.get("inputUsername")
	password = request.form.get("inputPassword")
	# Make sure username does not exist.
	if db.execute("SELECT * FROM users WHERE username = :username", {"username": name}).rowcount != 0:
		return render_template("invalidUsername.html", username= name, password= password) #done
	
	if db.execute("SELECT * FROM users WHERE username = :username", {"username": name}).rowcount == 0:
		db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", 
		{"username": name, "password": password})
		db.commit()
		return render_template("success.html") #done
		
	
