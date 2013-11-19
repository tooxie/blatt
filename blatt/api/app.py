# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.restful import Api

from blatt.api.resources import (PublicationResource, ArticleResource,
                                 JournalistResource, MediaResource)

app = Flask(__name__)
app.config.from_object('blatt.api.config')
api = Api(app)

api.add_resource(PublicationResource, '/publications/',
                 '/publications/<int:obj_id>/', endpoint='publications')
api.add_resource(ArticleResource, '/articles/', '/articles/<int:obj_id>',
                 endpoint='articles')
api.add_resource(JournalistResource, '/journalists/',
                 '/journalists/<int:obj_id>', endpoint='journalists')
api.add_resource(MediaResource, '/media/', '/media/<int:obj_id>',
                 endpoint='media')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
