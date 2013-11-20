# -*- coding: utf-8 -*-
import hashlib

from wtforms.fields import StringField, PasswordField, BooleanField
from wtforms.form import Form
from wtforms.validators import InputRequired, Email, ValidationError
from wtforms.widgets import HiddenInput

from blatt.persistence import User, session
from blatt.www.formvalidators import EmailNotInUse, EmailExists
from blatt.www.widgets import InputWidget, PasswordWidget, CheckboxWidget

REQUIRED_MSG = u'Este campo es requerido.'
WRONG_LOGIN_MSG = u'El correo o la contraseña ingresados son incorrectos.'
PASSWORDS_DONT_MATCH = u'Las contraseñas no coinciden.'

SIGNUP_EMAIL_VALIDATORS = (
    InputRequired(REQUIRED_MSG),
    Email(u'Ingrese un e-mail válido.'),
    EmailNotInUse(),
)
LOGIN_EMAIL_VALIDATORS = (
    InputRequired(REQUIRED_MSG),
    EmailExists(WRONG_LOGIN_MSG)
)
PROFILE_EMAIL_VALIDATORS = (
    InputRequired(REQUIRED_MSG),
    Email(u'Ingrese un e-mail válido.'),
    EmailNotInUse(),
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


class ProfileForm(Form):
    name = StringField(u'Nombre', widget=InputWidget())
    email = StringField(u'e-Mail', widget=InputWidget(),
                        validators=PROFILE_EMAIL_VALIDATORS)
    new_password = PasswordField(u'Nuevo password', widget=PasswordWidget())
    new_password_again = PasswordField(u'Repita el password',
                                       widget=PasswordWidget())

    def validate_new_password_again(self, field):
        if self.new_password.data or field.data:
            if self.new_password.data != field.data:
                raise ValidationError(PASSWORDS_DONT_MATCH)


class ProfileConfirmationForm(Form):
    current_password = StringField(u'Password', widget=PasswordWidget())

    name = StringField(u'Nombre', widget=HiddenInput())
    email = StringField(u'e-Mail', widget=HiddenInput())
    new_password = StringField(u'Nuevo password', widget=HiddenInput())
    signature = StringField(widget=HiddenInput())

    def __init__(self, formdata, **kwargs):
        self.secret_key = kwargs.pop('secret_key')

        super(ProfileConfirmationForm, self).__init__(formdata, **kwargs)

    def sign(self):
        self.signature.data = self.get_signature()

    def get_signature(self):
        sig = u'%(name)r$%(email)r$%(password)r$%(secret_key)r' % {
            'name': self.name.data,
            'email': self.email.data,
            'password': self.new_password.data,
            'secret_key': self.secret_key,
        }

        return hashlib.md5(unicode(sig)).hexdigest()

    def validate_signature(self, field):
        if field.data != self.get_signature():
            raise ValidationError(u'Error desconocido')
