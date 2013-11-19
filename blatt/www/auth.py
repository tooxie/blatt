# -*- coding: utf-8 -*-
from flask.ext.login import LoginManager

from blatt.persistence import User, session

login_manager = LoginManager()


def register_login_manager(app):
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    try:
        return session.query(User).get(user_id)
    except:
        return None
