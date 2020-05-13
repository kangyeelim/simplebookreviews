# simplebookreviews

## Try it out
https://simplebookreview.herokuapp.com/

## Usage

* Register an account
* Search books by name, author or ISBN
* Get info about a book
* Submit your own ratings and review!

## :gear: Setup your own

```bash
# Clone repo
$ git clone this repository

$ cd simplebookreviews

# Install all dependencies
$ pip install -r requirements.txt

# ENV Variables
$ export FLASK_APP = application.py # flask run
$ export DATABASE_URL = Heroku Postgres DB URI
$ export GOODREADS_KEY = Goodreads API Key. # More info: https://www.goodreads.com/api

#To run application
$ flask run

#Go to the ip address on browser (http://127.0.0.1:5000/)
```

### DB Schema

Feel free to add your own improvements!

| Schema |      Name      |   Type   |     Owner   |
|--------|----------------|----------|-------------|
| public | books          | table    |             |
| public | books_id_seq   | sequence |  		   |
| public | reviews        | table    |  |
| public | reviews_id_seq | sequence |  |
| public | users          | table    |  |
| public | users_id_seq   | sequence |  |

(6 rows)

Table "public.books"
|Column |       Type        | Collation | Nullable |              Default              |
|------|------------------|----------|---------|----------------------------------|
| id    | integer           |           | not null | nextval('books_id_seq'::regclass) |
| isbn  | character varying |           | not null |								   |
| title | character varying |           | not null |								   |
| author| character varying |           | not null |								   |
| year  | character varying |           | not null |								   |

Indexes:
    "books_pkey" PRIMARY KEY, btree (id)
	
Table "public.reviews"
|  Column  |       Type        | Collation | Nullable |               Default|
|---------|-------------------|-----------|----------|------------------------------------|
| id       | integer           |           | not null | nextval('reviews_id_seq'::regclass)|
| review   | text              |           | not null ||
| username | character varying |           | not null ||
| user_id  | integer           |           | not null ||
| rating   | character varying |           | not null ||
| book_id  | integer           |           | not null ||

Indexes:
    "reviews_pkey" PRIMARY KEY, btree (id)
	
Table "public.users"
 | Column  |       Type        | Collation | Nullable |              Default|
|---------|-------------------|-----------|----------|----------------------------------|
| id       | integer           |           | not null | nextval('users_id_seq'::regclass)|
| username | character varying |           | not null ||
| password | character varying |           | not null ||

Indexes:
    "users_pkey" PRIMARY KEY, btree (id)	