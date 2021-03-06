# -*- coding: utf-8 -*-
from math import ceil

from flask import request
from flask.ext.restful import Resource, marshal, abort


class BlattResource(Resource):
    def __init__(self, *args, **kwargs):
        self.options = None

        super(BlattResource, self).__init__(*args, **kwargs)

    def get(self, obj_id=None):
        if obj_id:
            return self._one(obj_id)

        return self._all()


    def _one(self, obj_id):
        try:
            result = self.get_one(obj_id)
        except:
            abort(404)

        return marshal(result, self.get_fields())

    def _all(self):
        result = self.get_all()

        return self.paginate(result)

    def get_options(self):
        if not self.options:
            self.options = request.args.to_dict()

        return self.options

    def apply_filters(self, queryset):
        """
        This method is supposed to be overriden by its children, to define the
        options available and how to map them to a DB field. The format is as
        follows:

        (
            ('db_field', 'field'),
            ('publication_pk', 'publication'),
        )

        It reads "filter by publication_pk, as publication in the GET query".
        """

        options = self.get_options()
        if not hasattr(self, 'get_filters'):
            return queryset

        for attribute in self.get_filters():
            key = attribute[0]
            value = options.get(attribute[1])
            if value:
                queryset = queryset.filter_by(**{key: value})

        if hasattr(self, 'filter') and callable(self.filter):
            queryset = self.filter(queryset, options)
            if not queryset:
                return []

        return queryset

    def paginate(self, queryset):
        options = self.get_options()
        queryset = self.apply_filters(queryset)

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
            'page_size': limit,
            'pages': total_pages,
        }
