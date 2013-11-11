# -*- coding: utf-8 -*-
def any_dict(_dict):
    for key, val in _dict.iteritems():
        if val:
            return True

def not_empty(_dict):
    values = {}
    for key, val in _dict.iteritems():
        if val:
            values[key] = val

    return values
