# -*- coding: utf-8 -*-
from wtforms.fields import StringField, PasswordField, BooleanField
from wtforms.form import Form
from wtforms.validators import InputRequired, Email, ValidationError

from blatt.persistence import User, session
from blatt.www.formvalidators import EmailNotInUse, EmailExists
from blatt.www.widgets import InputWidget, PasswordWidget, CheckboxWidget

REQUIRED_MSG = u'Este campo es requerido.'
WRONG_LOGIN_MSG = u'El correo o la contraseña ingresados son incorrectos.'

SIGNUP_EMAIL_VALIDATORS = (
    InputRequired(REQUIRED_MSG),
    Email(u'Ingrese un e-mail válido.'),
    EmailNotInUse(),
)
LOGIN_EMAIL_VALIDATORS = (
    InputRequired(REQUIRED_MSG),
    EmailExists(WRONG_LOGIN_MSG)
)


class SignupForm(Form):
    email = StringField(u'e-Mail', widget=InputWidget(),
                        validators=SIGNUP_EMAIL_VALIDATORS)
    password = PasswordField(u'Password', widget=PasswordWidget(),
                             validators=[InputRequired(REQUIRED_MSG)])


class LoginForm(Form):
    email = StringField(u'e-Mail', widget=InputWidget(),
                        validators=[InputRequired(REQUIRED_MSG)])
    password = PasswordField(u'Password', widget=PasswordWidget(),
                             validators=[InputRequired(REQUIRED_MSG)])
    remember_me = BooleanField(u'Recordarme', widget=CheckboxWidget())

    def __init__(self, *args, **kwargs):
        self.secret_key = kwargs.pop('secret_key', None)

        return super(LoginForm, self).__init__(*args, **kwargs)

    def validate_password(self, field):
        email = self.email.data
        password = self.password.data
        try:
            self.user = session.query(User).filter_by(email=email).one()
        except:
            raise ValidationError(WRONG_LOGIN_MSG)

        _password = self.user.mk_password(password, self.secret_key)
        if _password != self.user.password:
            print('%s == %s' % (user.mk_password(password, self.secret_key),
                                user.password))
            raise ValidationError(WRONG_LOGIN_MSG)
