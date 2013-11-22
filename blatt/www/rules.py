# -*- coding: utf-8 -*-
from flask import render_template

from blatt.persistence import session, Publication, Section

# PUBLICATION = ('pu', ForeignKeyOperator)
# SECTION = ('se', ForeignKeyOperator)
# JOURNALIST = ('jo', ForeignKeyOperator)
# MEDIA = ('me', BooleanOperator)
# TITLE = ('ti', FullTextOperator)
# BODY = ('bo', FullTextOperator)
# GEO = ('ge', GeoOperator)


# Operators
class ForeignKeyOperator(object):
    pass


class BooleanOperator(object):
    pass


class FullTextOperator(object):
    pass


class GeoOperator(object):
    pass


class EqualsOperator(object):
    name = u'Es'

    def __str__(self):
        return self.name


class NotEqualsOperator(object):
    name = u'No es'

    def __str__(self):
        return self.name


# Sources
class PublicationSource(object):
    name = u'Publicación'
    operators = (
        EqualsOperator(),
        NotEqualsOperator(),
    )

    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return self.name

    def __html__(self):
        publications = session.query(Publication).all()
        html = render_template('source_publication.html',
                               publications=publications)

        return html


class SectionSource(object):
    name = u'Sección'
    operators = (
        EqualsOperator(),
        NotEqualsOperator(),
    )

    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return u'Section'

    def __html__(self):
        publications = session.query(Publication).all()
        html = render_template('source_section.html', publications=publications)

        return html


class JournalistSource(object):
    pass


class MediaSource(object):
    pass


class BodySource(object):
    pass


class GeolocationSource(object):
    pass


# Rules
class Rule(object):

    def __init__(self, source=None, operator=None, value=None, negated=False):
        self.source = source()
        self.operator = operator
        self.value = source(value)
        self.negated = negated

    def get_operators(self):
        return self.source.operators

    def get_value_picker(self):
        return 'DERP'

    def __html__(self):
        return render_template('rule.html', rule=self)


class RuleSet(object):
    negated = False
    rules = [Rule(source=PublicationSource), Rule(source=SectionSource)]
