# -*- coding: utf-8 -*-
from blatt.markdownify import markdownify

from .exceptions import MultipleMatchesError


def extract(article, selector):
    content = article.select(selector).extract()
    length = len(content)

    if length == 1:
        return content[0].strip()
    elif length > 1:
        import ipdb; ipdb.set_trace()
        raise MultipleMatchesError(selector)

    return ''


def to_markup(html):
    return markdownify(html)
