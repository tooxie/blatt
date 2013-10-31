# -*- coding: utf-8 -*-
from datetime import datetime
import re

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.selector import XPathSelector
from slugify import slugify

from blatt.scrapers.spiders.utils import extract, to_markup
from blatt.scrapers.items import Article, Media

ALT_RE = re.compile(r'[()]|[aA]dhoc|[fF]oto')
SECTIONS = (
    (u'política', u'Política'),
    (u'economía', u'Economía'),
    (u'sociedad', u'Sociedad'),
    (u'justicia', u'Justicia'),
    (u'que vida', u'Que vida!'),
    (u'tribuna', u'Tribuna'),
    (u'mundo', u'Mundo'),
    (u'ciencia', u'Ciencia'),
    (u'región', u'Región'),
    (u'opinión', u'Opinion'),
    (u'empresas', u'Empresas'),
    (u'campo &amp; mercado', u'Campo y mercado'),
    (u'ideario', u'Ideario'),
    (u'interior', u'Interior'),
    (u'urbano', u'Urbano'),
    (u'la república de las mujeres', u'La república de las mujeres'),
)


class LaRepublicaSpider(CrawlSpider):
    name = 'larepublica'
    publication_name = u'La República'
    url = 'http://republica.com.uy'  # Custom field
    logo = ('http://www.republica.com.uy/wp-content/themes/la_republica_2013/'
            'images/logo_grande.png')
    allowed_domains = ['republica.com.uy']
    start_urls = [
        'http://www.republica.com.uy/'
    ]
    rules = (
        Rule(SgmlLinkExtractor(allow=r'/politica/.*')),
        Rule(SgmlLinkExtractor(allow=r'/economia/.*')),
        Rule(SgmlLinkExtractor(allow=r'/sociedad/.*')),
        Rule(SgmlLinkExtractor(allow=r'/justicia/.*')),
        Rule(SgmlLinkExtractor(allow=r'/que-vida/.*')),
        Rule(SgmlLinkExtractor(allow=r'/tribuna/.*')),
        Rule(SgmlLinkExtractor(allow=r'/mundo/.*')),
        Rule(SgmlLinkExtractor(allow=r'/region/.*')),
        Rule(SgmlLinkExtractor(allow=r'/opinion/.*')),
        Rule(SgmlLinkExtractor(allow=r'/suplementos/.*')),
        Rule(SgmlLinkExtractor(allow=r'/.*',
                               deny=[r'/horoscopo/.*',r'/videos/.*',
                                     r'/blogs/.*', r'/adrotate-out.php.*']),
             callback='parse_article'),
    )

    def parse_article(self, response):
        selector = XPathSelector(response)

        title = selector.select('//div[@class="colmask cols2"]'
                                '/*/h1/text()').extract()[0]
        date = parse_date(selector.select('//p[@class="leyenda_foto"]/text()'))
        deck = parse_deck(selector.select('//p[@class="colgado"]/text()'))
        lead = selector.select('//p[@class="excerpt_single"]'
                               '/text()').extract()[0]
        img = selector.select('//div[@class="img"]')
        media = [mk_media(img)] if exists(img) else []

        author = [author.strip() for author in \
                  selector.select('//div[@class="autor"]/p/text()').extract()]
        section = parse_section(selector)
        body = parse_body(selector.select('//div[@class="content_single"]/p'))

        return Article(url=response.url, title=title, deck=deck, lead=lead,
                       body=body, authors=author, media=media,
                       section=section, date=date)


def parse_body(paragraphs):
    body = ''

    for element in paragraphs.extract():
        body += to_markup(element)

    return body.strip()


def parse_deck(match):
    deck = None
    match = match.extract()

    if match:
        deck = match[0].strip()

    for section in SECTIONS:
        if section[0] == deck.lower():
            deck = None

    return deck


def parse_date(match):
    # 'Publicado el 27/10/2013 - 11:34'
    timestamp = match.extract()[0]

    return datetime.strptime(timestamp, 'Publicado el %d/%m/%Y - %H:%M')


def exists(img):
    if not img:
        return False

    return len(img.select('img')) > 0


# It's not considering some videos:
# http://www.republica.com.uy/una-joyita-turca/
# http://www.republica.com.uy/polemica-entre-alfredo-casero-y-estela-de-carlotto/
def mk_media(img):
    url = img.select('img/@src').extract()[0]
    caption = img.select('img/@alt').extract()[0].strip()
    author = img.select('p[@class="credito_foto"]/text()').extract()
    if author:
        author = author[0].strip()

    return Media(url=url, caption=caption, photographer=author)


def parse_section(selector):
    _section = 'Sin sección'

    # <meta name="keywords">
    meta = selector.select('//meta[@name="keywords"]/@content').extract()
    for keywords in meta:
        for section in SECTIONS:
            if section[0] in keywords:
                _section = section[1]

    # <div class="colgado">
    section = selector.select('//p[@class="colgado"]/text()').extract()
    if section:
        section = section[0]
        if slugify(unicode(section)) == 'opinion':
            _section = section

    return _section
