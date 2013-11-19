# -*- coding: utf-8 -*-
import re

from flask.ext.login import current_user
from markdown import markdown
from slugify import slugify

TWIT_RE = re.compile(r'@([A-Za-z0-9_]+)')


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
    author = media.photographer.name if media.photographer else ''

    if caption:
        if author:
            caption = u'%s (Foto: %s)' % (caption, author)
    else:
        if author:
            caption = u'Foto: %s' % author

    return caption


def get_article_image(article):
    if len(article.medias):
        return article.medias[0].url

    return ''


def twitterify(string):
    return TWIT_RE.sub('<a href="https://twitter.com/\\1">@\\1</a>', string)


def get_user():
    if current_user.is_anonymous():
        return None

    return current_user


def register_filters(app):
    app.jinja_env.filters['get_caption'] = get_media_caption
    app.jinja_env.filters['get_image'] = get_article_image
    app.jinja_env.filters['get_lead'] = get_article_lead
    app.jinja_env.filters['markdown'] = markdown
    app.jinja_env.filters['slugify'] = slugify
    app.jinja_env.filters['len'] = len
    app.jinja_env.filters['str'] = str
    app.jinja_env.filters['twitterify'] = twitterify
    app.jinja_env.filters['split'] = lambda x: x.split('@')[0]
