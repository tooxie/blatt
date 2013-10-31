# -*- coding: utf-8 -*-
import re

from blatt.markdownify import markdownify
from blatt.scrapers.spiders.exceptions import MultipleMatchesError

COMM_RE = re.compile(r'<!--.*-->', re.M + re.S)


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
    html = COMM_RE.sub('', html)

    return markdownify(html)
