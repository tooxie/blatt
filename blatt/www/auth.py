# -*- coding: utf-8 -*-
from flask.ext.login import LoginManager
from sqlalchemy.orm.exc import NoResultFound

from blatt.persistence import User, session

login_manager = LoginManager()


def register_login_manager(app):
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = u'Necesita identificarse para poder acceder'


@login_manager.user_loader
def load_user(user_id):
    try:
        return session.query(User).get(user_id)
    except NoResultFound:
        return None
