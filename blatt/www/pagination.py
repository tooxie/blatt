# -*- coding: utf-8 -*-
from math import floor

from flask import render_template, Markup


class Pagination(object):

    def __init__(self, page, per_page, total_count,
                 template='pagination.html'):
        self.page = int(page)
        self.per_page = int(per_page)
        self.total_count = int(total_count)
        self.template = template

    @property
    def pages(self):
        return int(floor(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=3, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

    def __html__(self):
        return Markup(render_template(self.template, pagination=self))
