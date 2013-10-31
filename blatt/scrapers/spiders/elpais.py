# -*- coding: utf-8 -*-
from datetime import datetime
import re

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.selector import XPathSelector

from blatt.scrapers.spiders.utils import extract, to_markup
from blatt.scrapers.items import Article, Media

MONTHS = {
    'ene': '1',
    'jan': '1',
    'feb': '2',
    'mar': '3',
    'abr': '4',
    'apr': '4',
    'may': '5',
    'jun': '6',
    'jul': '7',
    'ago': '8',
    'aug': '8',
    'sep': '9',
    'set': '9',
    'oct': '10',
    'nov': '11',
    'dic': '12',
    'dec': '12',
}


class ElPaisSpider(CrawlSpider):
    name = 'elpais'
    publication_name = u'El País'
    url = 'http://www.elpais.com.uy'  # Custom field
    allowed_domains = ['www.elpais.com.uy', 'www.ovaciondigital.com.uy']
    start_urls = [
        'http://www.elpais.com.uy/',
        'http://www.ovaciondigital.com.uy/'
    ]
    rules = (
        Rule(SgmlLinkExtractor(allow=r'.*\.html'), callback='parse_article'),
        Rule(SgmlLinkExtractor(allow=r'/.*/', deny=[r'/ecos/.*',
                                                    r'/se-dice/.*',
                                                    r'/sociales/.*'])),
    )

    def parse_article(self, response):
        selector = XPathSelector(response)

        title = extract(selector.select('//div[@class="title"]/h1/text()'))
        deck = extract(selector.select('//div[@class="supra"]/h2/text()'))
        lead = extract(selector.select('//div[@class="pc"]/p/text()'))
        date = parse_date(selector.select('//span[@class="published"]/text()'))
        body = parse_body(selector.select('//div[@class="article-content"]/p'))
        media = get_media(selector, self.url)
        author = extract(selector.select('//div[@class="signature"]/text()'))
        authors = [author] if author else []
        section = extract(selector.select('//div[@class="middle-content"]'
                                          '/a/text()'), default=u'Deportes')

        return Article(url=response.url, title=title, deck=deck, lead=lead,
                       body=body, authors=author, media=media,
                       section=section, date=date)


def extract(element, default=None):
    value = ''
    try:
        value = element.extract()[0].strip()
    except IndexError:
        value = default or ''

    return value


def parse_date(element):
    if len(element) == 0:
        return None

    timestamp = element.extract()[0].lower()
    timestamp = timestamp[timestamp.find(' ')+1:]
    if timestamp.endswith('cet'):
        timestamp = timestamp[:-4]

    # Special cases... #facepalm
    # http://www.ovaciondigital.com.uy/futbol/dio-vuelta-honor.html
    # http://www.ovaciondigital.com.uy/futbol/fenix-salio-pozo.html
    # http://www.elpais.com.uy/economia/noticias/gasto-privado-consumo-pib-2012.html
    if timestamp.startswith('apr 2013'):
        timestamp = timestamp.replace('apr', 'apr 1')
    elif timestamp.startswith('mar 2013'):
        timestamp = timestamp.replace('mar', 'mar 1')

    for month in MONTHS.keys():
        if timestamp.startswith(month):
            timestamp = timestamp.replace(month, MONTHS[month])

    if ':' in timestamp:
        date_format = '%m %d %Y %H:%M'
    else:
        date_format = '%m %d %Y'

    return datetime.strptime(timestamp, date_format)


def parse_body(paragraphs):
    body = ''

    for p in paragraphs:
        _class = p.select('@class').extract()
        if len(_class) == 0 or (_class[0] != 'article-ad'):
            body += to_markup(p.extract())

    return body


# Videos?
# http://www.elpais.com.uy/informacion/ejecutivo-podra-reducir-iva-puntos.html
def get_media(selector, host):
    media = []
    author = ''
    caption = ''
    div = selector.select('//div[@class="box-big-border-content"]')

    if div.select('div[contains(@class, "slider")]'):
        for slide in div.select('.//div[@class="slide"]').extract():
            url = host + slide.select('.//img/@src').extract()[0]
            content = slide.select('.//div[@class="description-text"]'
                                   '/div/text()').extract()

            content = content[0].strip()

            caption, author = parse_caption(content)

            media.append(Media(url=url, caption=caption, photographer=author))
    elif div.select('div[contains(@class, "image")]'):
        img = div.select('.//img')
        if img:
            url = host + img.select('@src').extract()[0]

        content = div.select('.//div[@class="description-overlay-image"]/p')
        if content:
            content = content.select('text()').extract()
            if content:
                caption, author = parse_caption(content[0].strip())

        media.append(Media(url=url, caption=caption, photographer=author))

    return media


def parse_caption(content):
    caption = ''
    author = ''

    if 'Foto:' in content:
        if content.startswith('Foto:'):
            author = content[6:]
        else:
            _content = [bit.strip() for bit in content.split('Foto:')]
            caption, author = (_content[0], _content[-1])

    return (caption, author)
