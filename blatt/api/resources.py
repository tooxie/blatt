# -*- coding: utf-8 -*-
from flask.ext.restful import fields

from blatt.api.fields import (RelatedResource, Geolocation, InstanceURL,
                              ForeignKeyField)
from blatt.api.restful import BlattResource
from blatt.persistence import session, Publication, Article, Journalist, Media


class ArticleResource(BlattResource):
    def get_filters(self):
        return (
            ('publication_pk', 'publication'),
            ('section_pk', 'section'),
        )

    def get_fields(self):
        return {
            'pk': fields.String,
            'title': fields.String,
            'deck': fields.String(''),
            'lead': fields.String(''),
            'body': fields.String,
            'url': fields.String,
            'geolocation': Geolocation('latitude', 'longitude'),
            'publication_date': fields.DateTime,
            'publication': ForeignKeyField('publications', ['name']),
            'section': ForeignKeyField('sections', ['name']),
            'authors': ForeignKeyField('journalists', ['name']),
            'media': ForeignKeyField('/media/'),
        }

    def filter(self, queryset, options):
        j_id = options.get('journalist')
        if j_id:
            queryset = queryset.filter(Article.authors.any(pk=j_id))

        return queryset

    def get_one(self, art_id, options=None):
        return session.query(Article).get(art_id)

    def get_all(self):
        return session.query(Article)


class PublicationResource(BlattResource):
    def get_fields(self):
        return {
            'pk': fields.String,
            'name': fields.String,
            'slug': fields.String,
            'logo': fields.String,
            'website': fields.String(attribute='url'),
            'url': InstanceURL('publications'),
            'articles': RelatedResource('/articles/', 'publication'),
        }

    def get_one(self, pub_id, options=None):
        return session.query(Publication).get(pub_id)

    def get_all(self):
        return session.query(Publication)


class JournalistResource(BlattResource):
    def get_fields(self):
        return {
            'pk': fields.String,
            'name': fields.String,
            'url': InstanceURL('journalists'),
            'articles': RelatedResource('/articles/', 'journalist'),
        }

    def get_one(self, j_id, options=None):
        return session.query(Journalist).get(j_id)

    def get_all(self):
        return session.query(Journalist)


class MediaResource(BlattResource):
    def get_fields(self):
        return {
            'url': InstanceURL('media'),
            'image': fields.String(attribute='url'),
            'caption': fields.String,
            'article': ForeignKeyField('articles'),
            'photographer': ForeignKeyField('photographers'),
        }

    def get_one(self, media_id, options=None):
        return session.query(Media).get(media_id)

    def get_all(self):
        return session.query(Media)
