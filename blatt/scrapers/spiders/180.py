# -*- coding: utf-8 -*-
from datetime import datetime
import re

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.selector import XPathSelector

from blatt.scrapers.spiders.utils import extract, to_markup
from blatt.scrapers.items import Article, Media

ALT_RE = re.compile(r'[()]|[aA]dhoc|[fF]oto')
MONTHS = {
    'enero': '1',
    'febrero': '2',
    'marzo': '3',
    'abril': '4',
    'mayo': '5',
    'junio': '6',
    'julio': '7',
    'agosto': '8',
    'setiembre': '9',
    'octubre': '10',
    'noviembre': '11',
    'diciembre': '12'
}



class Portal180Spider(CrawlSpider):
    name = '180'
    publication_name = u'180.com.uy'
    url = 'http://180.com.uy'  # Custom field
    logo = 'http://180.com.uy/tplef/img/logo.gif'  # Custom field
    allowed_domains = ['180.com.uy']
    start_urls = [
        'http://180.com.uy/'
    ]
    rules = (
        Rule(SgmlLinkExtractor(allow=r'/actualidad/.*')),
        Rule(SgmlLinkExtractor(allow=r'/deportes/.*')),
        Rule(SgmlLinkExtractor(allow=r'/darwin/.*')),
        Rule(SgmlLinkExtractor(allow=r'/galeria/.*')),
        Rule(SgmlLinkExtractor(allow=r'/articulo/.*'),
             callback='parse_article'),
    )

    def parse_article(self, response):
        selector = XPathSelector(response)
        article = selector.select('//div[contains(@class, "tef-md-seccion")]')

        title = extract(article, 'div[@class="hd"]/h2/text()')
        deck = selector.select('//div[@class="hd"]'
                               '/p/text()').extract()[0].strip()
        date = get_date(article.select('div[@class="hd"]/p/text()').extract())
        authors = selector.select('//a[contains(@href, "/periodistas/")]/'
                                  'text()').extract()
        img = selector.select('//div[@class="img"]/*/img')
        media = [mk_media(img)] if img else []
        section = selector.select('//h4/text()').extract()[0]

        body = parse_body(selector.select('//div[@class="mg"]/p'))

        return Article(url=response.url, title=title, deck=deck, body=body,
                       authors=authors, media=media, section=section,
                       date=date)


def parse_body(pp):
    body = ''

    for p in pp:
        if p.select('text()').extract():
            body += to_markup(p.extract())

    return body.strip()


def mk_media(img):
    url = img.select('@src').extract()[0]
    alt = img.select('@alt').extract()[0]
    caption = alt[:alt.rfind('(')].strip()
    author = ALT_RE.sub('', alt[alt.rfind('('):-1]).strip()

    return Media(url=url, caption=caption, photographer=author)


def get_date(results):
    # Example match: 'Publicado el: 27 de octubre de 2013 a las 14:14'
    for match in results:
        if match.startswith('Publicado el:'):
            for month in MONTHS.keys():
                if month in match:
                    match = match.replace(month, MONTHS[month])

            date = match[14:]

            return datetime.strptime(date, '%d de %m de %Y a las %H:%M')
