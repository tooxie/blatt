# -*- coding: utf-8 -*-
from flask import Flask, render_template, abort, request, redirect, url_for
from flask.ext.login import login_user, logout_user, current_user

from blatt.persistence import session, Publication, Article, User
from blatt.www.jinjafilters import register_filters
from blatt.www.auth import register_login_manager
from blatt.www.forms import LoginForm, SignupForm

app = Flask(__name__)
app.config.from_object('blatt.www.config')


@app.route('/')
def index():
    publications = session.query(Publication).all()

    return render_template('publication_list.html', publications=publications)


@app.route('/about/')
def about():
    publications = session.query(Publication).all()

    return render_template('about.html', publications=publications)


@app.route('/<slug>/')
def publication_detail(slug):
    publications = session.query(Publication).all()
    try:
        publication = session.query(Publication).filter_by(slug=slug).one()
    except:
        abort(404)

    articles = session.query(Article).filter_by(
        publication=publication).order_by(
            Article.publication_date.desc(), Article.title).limit(30)

    return render_template('publication_detail.html', publication=publication,
                           articles=articles, publications=publications)


class Map:
    def __init__(self, article):
        self.latitude = article.latitude
        self.longitude = article.longitude
        self.api_key = app.config.get('GOOGLE_MAPS_API_KEY')
        self.mark_title = article.title

    def render(self):
        return render_template('gmaps.html', latitude=self.latitude,
                               longitude=self.longitude, api_key=self.api_key,
                               title=self.mark_title)


@app.route('/<publication_slug>/<article_slug>/<int:article_pk>/')
def article_detail(publication_slug, article_slug, article_pk):
    publications = session.query(Publication).all()
    map = None
    article = session.query(Article).get(article_pk)
    if not article:
        abort(404)

    try:
        publication = session.query(Publication).filter_by(
            slug=publication_slug).one()
    except:
        abort(404)

    if article.latitude and article.longitude:
        map = Map(article)

    return render_template('article_detail.html', publication=publication,
                           article=article, map=map, publications=publications)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if not current_user.is_anonymous():
        return redirect('/')

    login_form = LoginForm(request.form, secret_key=app.config['SECRET_KEY'])

    if request.method == 'POST' and login_form.validate():
        email = request.form.get('email')
        password = request.form.get('password', '')

        user = session.query(User).filter_by(email=email).one()

        login_user(user)
        return redirect('/')

    return render_template('login.html', form=login_form)

@app.route("/logout/")
def logout():
    logout_user()

    return render_template('logout.html')

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if not current_user.is_anonymous():
        return redirect('/')

    signup_form = SignupForm(request.form)

    if request.method == 'POST' and signup_form.validate():
        email = request.form.get('email')
        password = request.form.get('password', '')

        user = User(email=email)
        user.set_password(password, app.config['SECRET_KEY'])

        session.add(user)
        session.commit()

        return redirect('/signup/done/')

    return render_template('signup.html', form=signup_form)

@app.route('/password-recovery/')
def password_recovery():
    return render_template('password_recovery.html')

@app.route('/signup/done/')
def signup_done():
    return render_template('signup_done.html')

register_login_manager(app)
register_filters(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
