# -*- coding: utf-8 -*-
from flask import render_template
from flask.ext.login import current_user
from wtforms.validators import Email, ValidationError

from blatt.persistence import User, session


class EmailNotInUse(Email):
    def __call__(self, form, field, **kwargs):
        super(EmailNotInUse, self).__call__(form, field, **kwargs)

        email = field.data
        queryset = session.query(User).filter_by(email=email)
        if not current_user.is_anonymous():
            queryset = queryset.filter(User.email != current_user.email)

        if queryset.count() != 0:
            raise ValidationError(render_template('email_in_use.html'))


class EmailExists(Email):
    def __call__(self, form, field, **kwargs):
        super(EmailExists, self).__call__(form, field, **kwargs)

        email = field.data

        if session.query(User).filter_by(email=email).count() != 1:
            raise ValidationError(self.message)
