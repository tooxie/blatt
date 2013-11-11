# -*- coding: utf-8 -*-
from flask.ext.restful import marshal
from flask.ext.restful.fields import String, Raw


class RelatedResource(String):
    def __init__(self, endpoint, arg_name):
        self.endpoint = endpoint
        self.arg_name = arg_name

        super(RelatedResource, self).__init__(self, 'pk')

    def format(self, value):
        return '%s?%s=%s' % (self.endpoint, self.arg_name, value)


class Geolocation(Raw):
    def __init__(self, lat_field, lng_field):
        self.lat_field = lat_field
        self.lng_field = lng_field

    def output(self, key, obj):
        lat = getattr(obj, self.lat_field)
        lng = getattr(obj, self.lng_field)

        if lat and lng:
            return {'latitude': lat, 'longitude': lng}

        return None


class InstanceURL(String):
    def __init__(self, url):
        self.url = url

        super(InstanceURL, self).__init__(self, 'pk')

    def format(self, value):
        return '/%s/%i' % (self.url.strip('/'), value)


class ForeignKeyField(String):
    def __init__(self, endpoint, fields=None):
        default_fields = {
            'pk': String,
            'url': InstanceURL(endpoint),
        }

        if fields:
            [default_fields.update({key: String}) for key in fields]

        self.fields = default_fields

        super(ForeignKeyField, self).__init__()

    def format(self, obj):
        return marshal(obj, self.fields)
