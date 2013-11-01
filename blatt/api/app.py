# -*- coding: utf-8 -*-
from math import ceil

from flask import Flask, request
from flask.ext.restful import Api, Resource, marshal, fields, abort

from blatt.persistence import session, Publication, Article
from blatt.api.fields import (RelatedResource, Geolocation, InstanceURL,
                              ForeignKeyField)

app = Flask(__name__)
api = Api(app)


class BlattResource(Resource):
    def get(self, obj_id=None):
        options = request.args.to_dict()
        if obj_id:
            try:
                result = self.get_one(obj_id)
            except:
                abort(404)
        else:
            result = self.get_all(options)

        if obj_id:
            return marshal(result, self.get_fields())

        return self.paginate(result)

    def paginate(self, queryset):
        options = request.args.to_dict()

        try:
            page_number = int(options.get('page', 1))
        except ValueError:
            page_number = 1
        try:
            limit = int(options.get('page_size', 10))
        except ValueError:
            limit = 10
        offset = limit * (page_number - 1)

        count = queryset.count()
        total_pages = max(ceil(float(count) / float(limit)), 1)
        items = queryset.limit(limit).offset(offset).all()

        return {
            'item_count': count,
            'items': marshal(items, self.get_fields()),
            'page': page_number,
            'pages': total_pages,
        }


class ArticleResource(BlattResource):
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
        }

    def get_one(self, art_id, options=None):
        return session.query(Article).get(art_id)

    def get_all(self, options=None):
        publication_pk = options.get('publication')

        articles = session.query(Article)

        if publication_pk:
            articles = articles.filter_by(publication_pk=publication_pk)

        return articles



class PublicationResource(BlattResource):
    def get_fields(self):
        return {
            'pk': fields.String,
            'name': fields.String,
            'slug': fields.String,
            'logo': fields.String,
            'url': fields.String,
            'articles': RelatedResource('/articles/', 'publication'),
        }

    def get_one(self, pub_id, options=None):
        return session.query(Publication).get(pub_id)

    def get_all(self, options=None):
        return session.query(Publication)


api.add_resource(PublicationResource, '/publications/',
                 '/publications/<int:obj_id>/')
api.add_resource(ArticleResource, '/articles/', '/articles/<int:obj_id>/')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
