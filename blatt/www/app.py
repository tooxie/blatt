# -*- coding: utf-8 -*-
from flask import Flask, render_template, abort
from slugify import slugify
from markdown import markdown

from blatt.persistence import session, Publication, Article

app = Flask(__name__)

@app.route('/')
def index():
    publications = session.query(Publication).all()

    return render_template('publication_list.html', publications=publications)

@app.route('/<slug>')
def publication_detail(slug):
    try:
        publication = session.query(Publication).filter_by(slug=slug).one()
    except:
        abort(404)

    articles = session.query(Article).filter_by(
        publication=publication).order_by(
            Article.publication_date.desc(), Article.title).limit(30)

    return render_template('publication_detail.html', publication=publication,
                           articles=articles)

@app.route('/<publication_slug>/<article_slug>/<int:article_pk>')
def article_detail(publication_slug, article_slug, article_pk):
    print('ARTICLE DETAIL')
    article = session.query(Article).get(article_pk)
    if not article:
        abort(404)

    try:
        publication = session.query(Publication).filter_by(
            slug=publication_slug).one()
    except:
        abort(404)

    return render_template('article_detail.html', publication=publication,
                           article=article)


def get_article_image(article):
    if len(article.medias):
        return article.medias[0].url

    return ''


def get_article_lead(article):
    lead = article.lead
    if not lead:
        lead = article.deck

    if not lead:
        lead = article.body[:article.body.find('.')]

    words = lead.split(' ')
    if len(words) > 20:
        lead = ' '.join(words[:20]) + '...'

    return lead


def get_media_caption(media):
    caption = media.caption or ''
    author = media.photographer.name or ''

    if caption:
        if author:
            caption = u'%s (Foto: %s)' % (caption, author)
    else:
        if author:
            caption = u'Foto: %s' % author

    return caption


app.jinja_env.filters['get_caption'] = get_media_caption
app.jinja_env.filters['get_image'] = get_article_image
app.jinja_env.filters['get_lead'] = get_article_lead
app.jinja_env.filters['markdown'] = markdown
app.jinja_env.filters['slugify'] = slugify
app.jinja_env.filters['len'] = len


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')