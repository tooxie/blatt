# -*- coding: utf-8 -*-
from math import ceil

from flask import request
from flask.ext.restful import Resource, marshal, abort


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

    def filter(self, queryset, filters):
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

        options = request.args.to_dict()
        filters = {}
        if not hasattr(self, 'get_filters'):
            return queryset

        for attribute in self.get_filters():
            key = attribute[0]
            value = options.get(attribute[1])
            if value:
                filters[key] = value

        if filters:
            queryset = queryset.filter_by(**filters)

        return queryset

    def paginate(self, queryset):
        options = request.args.to_dict()
        queryset = self.filter(queryset, options)

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
