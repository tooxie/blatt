# -*- coding: utf-8 -*-
from datetime import datetime
import re

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.selector import XPathSelector

from blatt.scrapers.spiders.utils import extract as _extract, to_markup
from blatt.scrapers.items import Article, Media

EXT_RE = re.compile(r'<div class="extension">(.*)</div>')
FOTO_RE = re.compile(r'[fF]oto:')


def extract(article, selector, md=True):
    content = _extract(article, selector)

    if '<div class="extension">' in content:
        extensions = ''.join(EXT_RE.findall(content))
        body = ''.join(EXT_RE.split(content))

        content = body + extensions

    if len(EXT_RE.findall(content)) > 1:
        import ipdb; ipdb.set_trace()

    if md:
        content = to_markup(content)

    return content.strip()


def parse_caption(string):
    string = string.strip()

    if not string:
        return (None, None)

    matches = [bit.strip() for bit in FOTO_RE.split(string)]

    if len(matches) > 2:
        matches = (matches[0], matches[-1])
    elif len(matches) == 1:
        return (string, None)

    caption, author = matches

    if caption == '':  # Means that string starts with the pattern "[fF]oto:"
        return (None, matches[1])

    if ',' in author:
        author = author.split(',')[0]

    return (caption, author)


class LaDiariaSpider(CrawlSpider):
    name = 'ladiaria'
    publication_name = u'la diaria'
    url = 'http://ladiaria.com.uy'  # Custom field
    logo = 'http://ladiaria.com.uy/media/img/ladiaria.jpg'  # Custom field
    allowed_domains = ['ladiaria.com', 'ladiaria.com.uy']
    start_urls = [
        'http://ladiaria.com.uy/'
    ]
    rules = (
        Rule(SgmlLinkExtractor(allow=r'/seccion/.*')),
        Rule(SgmlLinkExtractor(allow=r'/articulo/.*', deny=r'.*/discusion/'),
             callback='parse_article'),
    )

    def parse_article(self, response):
        selector = XPathSelector(response)
        article = selector.select('//div[@id="article"]')

        title = extract(article, 'h1/text()')
        deck = extract(article, 'p[@class="deck"]')
        lead = extract(article, 'p[@class="lead"]')
        body = extract(article, 'div[@id="body"]')
        date = extract(article, 'div[@class="titlebar"]/span[@class="date"]/text()')
        section = extract(article, 'div[@class="titlebar"]/h2/text()')

        authors = [author.strip() for author in \
            article.select('div[@class="byline"]/'
                           'span[@class="name"]/text()').extract()]

        media = [mk_media(media, self.url) for media in \
            selector.select('//a[@class="jbox" and '
                            '@rel="prettyPhoto[gallery]"]')]

        return Article(
            url=response.url, title=title, deck=deck, lead=lead, body=body,
            authors=authors, media=media, section=section,
            date=datetime.strptime(date, '%d.%m.%y'))


def mk_media(element, url):
    _url = url + extract(element, '@href', md=False)

    try:
        caption, author = parse_caption(extract(element, '@title', md=False))
    except Exception, e:
        import ipdb; ipdb.set_trace()

    media = Media(url=_url, caption=caption, photographer=author)

    return media
