import os
import requests
import json

from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
key = os.getenv("GOODREADS_KEY")
db = scoped_session(sessionmaker(bind=engine))
google_key = os.getenv("GOOGLE_KEY")

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
		user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": name, 
	"password": password}).fetchone()
		session["username"] = name
		reviews = db.execute("SELECT * FROM reviews WHERE username = :username", {"username": name}).fetchall()
		book_titles = db.execute("SELECT title FROM books, reviews WHERE books.id = book_id").fetchall()
		return render_template("home.html", user= user, reviews=reviews, book_titles=book_titles) #done
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

@app.route("/home/<int:id>")
def home(id):	
	if db.execute("SELECT * FROM users WHERE id = :id", {"id": id}).rowcount == 1:
		user = db.execute("SELECT * FROM users WHERE id = :id", {"id": id}).fetchone()
	if not session.get("username") is None:
		reviews = db.execute("SELECT * FROM reviews WHERE username = :username", {"username": user.username}).fetchall()
		book_titles = db.execute("SELECT title FROM books, reviews WHERE books.id = book_id").fetchall()
		return render_template("home.html", user= user, reviews=reviews, book_titles=book_titles)
	else:
		return redirect(url_for("index"))
	
@app.route("/bookspage/<int:id>")
def allbooks(id):
	if db.execute("SELECT * FROM users WHERE id = :id", {"id": id}).rowcount == 1:
		user = db.execute("SELECT * FROM users WHERE id = :id", {"id": id}).fetchone()
	books = db.execute("SELECT * FROM books").fetchall()
	if not session.get("username") is None:
		return render_template("bookspage.html", user=user, books=books)
	else:
		return redirect(url_for("index"))
		
@app.route("/search/<int:id>", methods=['POST'])
def search(id):
	input = request.form.get("input")
	books = db.execute("SELECT * FROM books WHERE title ILIKE :input OR isbn ILIKE :input OR author ILIKE :input OR year ILIKE :input",
	{"input": "%" + input + "%"}).fetchall()
	user = db.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": id}).fetchone()
	if not session.get("username") is None:
		return render_template("bookspage.html", user=user, books=books)
	else:
		return redirect(url_for("index"))
		
@app.route("/addbookbyisbn/<int:id>", methods=['POST'])
def addbookbyisbn(id):
	if session.get("username") is None:
		return redirect(url_for("index"))
	input = request.form.get("input")
	if len(input) != 10:
		flash('ISBN is a 10 character input', 'warning')
		return redirect("/bookspage/" + str(id))
	res = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + input + "&key=" + google_key)
	res = res.json()
	
	if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": input}).rowcount != 0:
		flash('The book is already in the library archive. Do a search to find it.', 'warning')
		return redirect("/bookspage/" + str(id)) #change to something proper
	try:
		for book in res["items"]:
			author = book["volumeInfo"]["authors"][0]
			isbn = input
			title = book["volumeInfo"]["title"]
			year = book["volumeInfo"]["publishedDate"]
			db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", 
			{"isbn": isbn, "title": title, "author": author, "year":year})
			db.commit()
		flash('Successfully added into library archive!')
		return redirect("/bookspage/" + str(id)) #change to something proper
	except KeyError:
		flash('Unable to add this book.')
		return redirect("/bookspage/" + str(id))
	except Error:
		flash('Oops something went wrong!')
		return redirect("/bookspage/" + str(id))

@app.route("/addbookbytitle/<int:id>", methods=['POST'])
def addbookbytitle(id):
	if session.get("username") is None:
		return redirect(url_for("index"))
	input = request.form.get("input")
	if db.execute("SELECT * FROM books WHERE title = :title", {"title": input}).rowcount != 0:
		flash('The book is already in the library archive. Do a search to find it.', 'warning')
		return redirect("/bookspage/" + str(id)) #change to something proper
	res = requests.get("https://www.googleapis.com/books/v1/volumes?q=intitle:" + input + "&key=" + google_key)
	res = res.json()
	try:
		book = res["items"][0]
		isbn = book["volumeInfo"]["industryIdentifiers"][1]["identifier"]
		if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).rowcount != 0:
			flash('The book is already in the library archive. Do a search to find it.', 'warning')
			return redirect("/bookspage/" + str(id)) #change to something proper	
		book = res["items"][0]
		author = book["volumeInfo"]["authors"][0]
		isbn = book["volumeInfo"]["industryIdentifiers"][1]["identifier"]
		title = book["volumeInfo"]["title"]
		year = book["volumeInfo"]["publishedDate"][0:4]
		db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", 
		{"isbn": isbn, "title": title, "author": author, "year":year})
		db.commit()
		flash('Successfully added into library archive!')
		return redirect("/bookspage/" + str(id))
	except KeyError:
		flash('Unable to add this book. Check if book already in the library.')
		return redirect("/bookspage/" + str(id))
	except Error:
		flash('Oops something went wrong!')
		return redirect("/bookspage/" + str(id))
		
@app.route("/book/<int:book_id>/<int:user_id>")
def book(book_id, user_id):
	if db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).rowcount == 1:
		book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
		isbn = book.isbn
	if not session.get("username") is None:
		res = requests.get("https://www.goodreads.com/book/review_counts.json", 
		params={"key": key, "isbns": isbn})
		res = res.json()
		info = res["books"][0]
		ave_rating = info["average_rating"]
		work_ratings_count = info["work_ratings_count"]
		work_reviews_count = info["work_reviews_count"]
		reviews = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id", {"user_id": user_id, "book_id": book_id})
		return render_template("book.html", book= book, ave_rating= ave_rating,
		ratings_count=work_ratings_count, reviews_count= work_reviews_count, user_id= user_id, reviews= reviews)
	else:
		return redirect(url_for("index"))

@app.route("/submitreview/<int:book_id>/<int:user_id>", methods=['POST'])
def submitreview(book_id, user_id):
	if db.execute("SELECT * FROM reviews WHERE user_id= :user_id AND book_id = :book_id", 
	{"user_id":user_id, "book_id":book_id}).rowcount != 0:
		flash('You have already submitted a review for this book.', 'warning')
		return redirect("/book/" + str(book_id) + "/" + str(user_id))
	if not session.get("username") is None:
		review = request.form.get("inputReview")
		rating = request.form.get("rating")
		username = db.execute("SELECT username FROM users WHERE id = :id", {"id": user_id}).fetchone()
		db.execute("INSERT INTO reviews (review, username, user_id, rating, book_id) VALUES (:review, :username, :user_id, :rating, :book_id)", 
		{"review": review, "username": username[0], "user_id": user_id, "rating": rating, "book_id": book_id})
		db.commit()
		return redirect("/book/" + str(book_id) + "/" + str(user_id))
	else:
		return redirect(url_for("index"))
	
	
@app.route("/account/<int:id>")
def account(id):
	if db.execute("SELECT * FROM users WHERE id = :id", {"id": id}).rowcount == 1:
		user = db.execute("SELECT * FROM users WHERE id = :id", {"id": id}).fetchone()
	if not session.get("username") is None:
		return render_template("account.html", user=user)
	else:
		return redirect(url_for("index"))
		
@app.route("/updateusername/<int:id>", methods=['POST'])
def updateusername(id):
	if session.get("username") is None:
		return redirect(url_for("index"))
	if db.execute("SELECT * FROM users WHERE id = :id", {"id": id}).rowcount == 1:
		user = db.execute("SELECT * FROM users WHERE id = :id", {"id": id}).fetchone()
		return render_template("updateusername.html", user=user)

@app.route("/changeusername/<int:id>", methods=['POST'])
def changeusername(id):
	if session.get("username") is None:
		return redirect(url_for("index"))
	newUsername = request.form.get("newUsername")
	if db.execute("SELECT * FROM users WHERE username = :username", {"username": newUsername}).rowcount != 0:
		flash('Username already used.', 'warning')
		#to do html!!!
		return redirect("/updateusername/" + str(id))
	if db.execute("SELECT * FROM users WHERE id = :id", {"id": id}).rowcount == 1:
		password = request.form.get("inputPassword")
		#update db only when id and password matches
		db.execute("UPDATE users SET username = :username WHERE id = :id AND password = :password" , {"username": newUsername, "id":id, "password": password})
		db.execute("UPDATE reviews SET username = :username WHERE user_id = :user_id" , {"username": newUsername, "id":id})
		db.commit()
		session.pop("username")
		return render_template("successchange.html")
	
@app.route("/updatepassword/<int:id>", methods=['POST'])	
def updatepassword(id):
	if session.get("username") is None:
		return redirect(url_for("index"))
	if db.execute("SELECT * FROM users WHERE id = :id", {"id": id}).rowcount == 1:
		user = db.execute("SELECT * FROM users WHERE id = :id", {"id": id}).fetchone()
		return render_template("updatepassword.html", user=user)
	
@app.route("/changepassword/<int:id>", methods=['POST'])
def changepassword(id):
	if session.get("username") is None:
		return redirect(url_for("index"))
	if db.execute("SELECT * FROM users WHERE id = :id", {"id": id}).rowcount == 1:
		user = db.execute("SELECT * FROM users WHERE id = :id", {"id": id}).fetchone()
		password = request.form.get("inputPassword")
		newPassword1 = request.form.get("newPassword1")
		newPassword2 = request.form.get("newPassword2")

		#update db only when id and password matches
		if newPassword1 == newPassword2:
			db.execute("UPDATE users SET password = :password WHERE id = :id AND username = :username" , {"username": session['username'], "id":id, "password": newPassword1})
			db.commit()
			session.pop("username")
			return render_template("successchange.html")
		else:
			flash('Mismatch for the 2 new password input.', 'warning')
			return redirect("/updatepassword/" + str(id))
			
@app.route('/signout', methods=['POST'])
def signout():
	session.pop("username")
	session.clear()
	return redirect(url_for("index"))
	
	
@app.route("/contact/<int:id>")
def contact(id):
	return render_template("contact.html", id=id)