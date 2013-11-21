# -*- coding: utf-8 -*-
from flask import (Flask, render_template, abort, request, redirect, url_for,
                   flash)
from flask.ext.login import (login_user, logout_user, current_user,
                             login_required)

from blatt.persistence import session, Publication, Article, User
from blatt.www.auth import register_login_manager
from blatt.www.forms import (LoginForm, SignupForm, ProfileForm,
                             ProfileConfirmationForm, SignedArticleForm)
from blatt.www.jinja import filters, functions
from blatt.www.pagination import Pagination

app = Flask(__name__)
app.config.from_object('blatt.www.config')


@app.route('/')
def index():
    return render_template('publication_list.html')


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/<slug>/')
def article_list(slug):
    try:
        publication = session.query(Publication).filter_by(slug=slug).one()
    except:
        abort(404)

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        page_size = int(request.args.get('page_size', 30))
    except ValueError:
        page_size = 30

    queryset = session.query(Article).filter_by(
        publication=publication).order_by(
            Article.publication_date.desc(), Article.title)

    count = queryset.count()
    articles = queryset.offset(page * page_size).limit(page_size)

    pagination = Pagination(page, page_size, count)

    return render_template('article_list.html', publication=publication,
                           articles=articles, pagination=pagination)


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
                           article=article, map=map)


@app.route('/social/', methods=['GET', 'POST'])
@login_required
def social():
    if request.method == 'GET':
        return redirect(request.args.get('next') or url_for('index'))

    secret_key = app.config['SECRET_KEY']
    signed_form = SignedArticleForm(request.form, secret_key=secret_key)
    article = signed_form._article
    if signed_form.validate():
        if 'like' in request.form:
            if article in current_user.liked_articles:
                current_user.liked_articles.remove(article)
            else:
                current_user.liked_articles.append(article)

            session.add(current_user)
            session.commit()

        return redirect(request.args.get('next') or request.referrer)

    abort(404)


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

        return redirect(request.args.get('next', '/'))

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
@login_required
def password_recovery():
    return render_template('password_recovery.html')

@app.route('/signup/done/')
def signup_done():
    return render_template('signup_done.html')

@app.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = ProfileForm(name=current_user.name,
                               email=current_user.email)

    if request.method == 'POST':
        profile_form = ProfileForm(request.form)

        if profile_form.validate():
            secret_key = app.config['SECRET_KEY']
            confirmation_form = ProfileConfirmationForm(request.form,
                                                        secret_key=secret_key)
            confirmation_form.sign()

            return render_template('profile_confirmation.html',
                                   form=confirmation_form)

    return render_template('profile.html', form=profile_form)

@app.route('/profile/confirm/', methods=['POST'])
@login_required
def profile_confirmation():
    secret_key = app.config['SECRET_KEY']
    confirmation_form = ProfileConfirmationForm(request.form,
                                                secret_key=secret_key)

    if confirmation_form.validate():
        current_user.name = request.form.get('name')
        current_user.email = request.form.get('email')

        if request.form.get('password'):
            current_user.set_password(request.form.get('password'))

        session.add(current_user)
        session.commit()

        flash(u'Perfil actualizado con éxito')

        return redirect('profile')

    return render_template('profile_confirmation.html', form=confirmation_form)

register_login_manager(app)
filters.register_filters(app)
functions.register_functions(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
