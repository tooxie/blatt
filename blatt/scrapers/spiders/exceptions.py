# -*- coding: utf-8 -*-
class MultipleMatchesError(Exception):
    def __init__(self, selector):
        msg = "The selector '%s' matches multiple elements" % str(selector)

        super(MultipleMatchesError, self).__init__(msg)

