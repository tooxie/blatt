# -*- coding: utf-8 -*-
from flask import render_template, Markup

from blatt.persistence import session, Publication
from blatt.www.forms import SignedArticleForm


class SocialMarkup(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, article):
        secret_key = self.app.config['SECRET_KEY']
        signed_form = SignedArticleForm(article=article, secret_key=secret_key)
        signed_form.sign()

        tpl = render_template('social.html', article=article, form=signed_form)

        return Markup(tpl)


def mk_carousel(article):
    tpl = render_template('carousel.html', article=article)

    return Markup(tpl)


def register_functions(app):
    app.jinja_env.globals.update({
        'get_publications': lambda: session.query(Publication).all(),
        'social_buttons': SocialMarkup(app),
        'carousel': mk_carousel,
        'len': len,
    })
