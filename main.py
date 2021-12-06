from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top-movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

API_KEY = 'e1def743d146a7aaffac7939941bf12c'

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
db.create_all()

class EditForm(FlaskForm):
    rating = FloatField(label="Your Rating Out of 10. e.g. 7.5", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Submit")

class AddForm(FlaskForm):
    title = StringField(label="Movie Title")
    add = SubmitField(label="Add Movie")

@app.route("/")
def home():
    all_movies = Movie.query.order_by('rating').all()
    i = len(all_movies)
    for movie in all_movies:
        movie.ranking = i
        i -= 1
    db.session.commit()
    print(type(all_movies))
    return render_template("index.html", all_movies=all_movies)

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    new_rating = EditForm()
    movie_id = request.args.get('id')
    print(movie_id)
    movie = Movie.query.get(movie_id)
    print(movie)
    if new_rating.validate_on_submit():
        movie.rating = new_rating.rating.data
        movie.review = new_rating.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=new_rating, movie=movie)

@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        title = form.title.data
        parameters = {
            "api_key": API_KEY,
            "query": title,
        }
        response = requests.get("https://api.themoviedb.org/3/search/movie", params=parameters)
        search_results = response.json()['results']
        return render_template('select.html', movies=search_results)
    return render_template('add.html', form=form)

@app.route("/select")
def select():
    movie_id = request.args.get('id')
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}", params={"api_key": API_KEY})
    movie_details = response.json()
    new_movie = Movie(
        title=movie_details['title'],
        year=movie_details['release_date'][0:4],
        description=movie_details['overview'],
        rating=0.0,
        ranking=0.0,
        review="None",
        img_url=f"https://image.tmdb.org/t/p/w500{movie_details['poster_path']}"
    )

    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True, port=2000)
