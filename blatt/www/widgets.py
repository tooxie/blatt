# -*- coding: utf-8 -*-
from wtforms.widgets import Input, PasswordInput, CheckboxInput


class InputWidget(Input):
    def __init__(self, error_class='error'):
        super(InputWidget, self).__init__(input_type='text')
        self.error_class = error_class

    def __call__(self, field, **kwargs):
        kwargs['class'] = 'form-control'
        kwargs['placeholder'] = field.label.text

        if field.errors and self.error_class:
            c = kwargs.pop('class', '') or kwargs.pop('class_', '')
            kwargs['class'] = u'%s %s' % (self.error_class, c)

        return super(InputWidget, self).__call__(field, **kwargs)


class PasswordWidget(PasswordInput):
    def __init__(self, error_class='error'):
        super(PasswordWidget, self).__init__()
        self.error_class = error_class

    def __call__(self, field, **kwargs):
        kwargs['class'] = 'form-control'
        kwargs['placeholder'] = field.label.text

        if field.errors:
            c = kwargs.pop('class', '') or kwargs.pop('class_', '')
            kwargs['class'] = u'%s %s' % (self.error_class, c)

        return super(PasswordWidget, self).__call__(field, **kwargs)


class CheckboxWidget(CheckboxInput):
    def __call__(self, field, **kwargs):
        checkbox = super(CheckboxWidget, self).__call__(field, **kwargs)

        return '<label class="checkbox">%(checkbox)s %(label)s</label>' % {
            'checkbox': checkbox, 'label': field.label.text
        }
