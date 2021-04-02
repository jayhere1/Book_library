from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
import gunicorn
import psycopg2
import os

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
# os.environ.get("DATABASE_URL", "sqlite:///MyBooks.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = os.environ.get("secret_key")


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    genre = db.Column(db.String(250), nullable=False)


db.create_all()


class AddBookForm(FlaskForm):
    id = StringField("What is the Book id", validators=[DataRequired()])
    title = StringField("What book do you want to add?", validators=[DataRequired()])
    author = StringField("Who is the author?", validators=[DataRequired()])
    genre = StringField("What is the genre?")
    submit = SubmitField("Done")


@app.route('/')
def home():
    all_books = db.session.query(Book).all()
    return render_template("index.html", books=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddBookForm()
    if request.method == "POST":
        if form.validate_on_submit():
            # CREATE RECORD
            new_book = Book(
                id=request.form["id"],
                title=request.form["title"],
                author=request.form["author"],
                genre=request.form["genre"]
            )
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('home'))
    else:
        return render_template("add.html", form=form)


@app.route("/delete", methods=["GET"])
def delete():
    book_id = request.args.get('id')
    book_to_delete = Book.query.get(book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

