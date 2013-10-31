# -*- coding: utf-8 -*-
from datetime import datetime
import re

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.selector import XPathSelector

from blatt.scrapers.spiders.utils import to_markup
from blatt.scrapers.items import Article, Media

GEO_RE = re.compile(r"GLatLng\('([\d\.-]+)', '([\d\.-]+)'\)")


class ElObservadorSpider(CrawlSpider):
    name = 'observa'
    publication_name = u'El Observador'
    url = 'http://elobservador.com.uy'
    logo = 'http://i.imgur.com/L8YxfD9.png'
    allowed_domains = ['elobservador.com.uy']
    start_urls = [
        'http://www.elobservador.com.uy/portada/'
    ]
    rules = (
        Rule(SgmlLinkExtractor(allow=r'/noticia/.*'),
             callback='parse_article'),

        # Secciones
        Rule(SgmlLinkExtractor(allow=r'/nacional/.*')),
        Rule(SgmlLinkExtractor(allow=r'/economia/.*')),
        Rule(SgmlLinkExtractor(allow=r'/mundo/.*')),
        Rule(SgmlLinkExtractor(allow=r'/agro/.*')),
        Rule(SgmlLinkExtractor(allow=r'/deportes/.*')),
        Rule(SgmlLinkExtractor(allow=r'/espectaculos/.*')),
        Rule(SgmlLinkExtractor(allow=r'/estilo/.*')),
        Rule(SgmlLinkExtractor(allow=r'/tecnologia/.*')),
        Rule(SgmlLinkExtractor(allow=r'/salud/.*')),
        Rule(SgmlLinkExtractor(allow=r'/opinion/.*')),
        Rule(SgmlLinkExtractor(allow=r'/videos/.*')),
        Rule(SgmlLinkExtractor(allow=r'/interactivos/.*')),
    )

    def parse_article(self, response):
        selector = XPathSelector(response)
        story = selector.select('//div[contains(@class, "story")]')

        title = selector.select('//h1/text()').extract()[0]
        deck = story.select('h2/text()').extract()[0]

        body = parse_body(selector.select('//div[@class="story_left"]/*'))
        authors = parse_author(selector.select('//div[@class="story_left"]'
                                               '/div[@class="fecha"]'))
        media = [mk_media(element) for element in \
            selector.select('//ul[@id="galeria-noticia-grande"]/li')]
        try:
            # Example: [u'Deportes - ']
            section = selector.select('//h5/b/text()').extract()[0][:-3]
        except Exception, e:
            import ipdb; ipdb.set_trace()
        date = get_date(selector.select('//div[@class="fecha"]'
                                        '/text()').extract())
        latitude, longitude = get_geolocation(response.body)

        return Article(url=response.url, title=title, deck=deck, body=body,
                       authors=authors, media=media, section=section,
                       latitude=latitude, longitude=longitude, date=date)


def get_geolocation(html):
    latitude = None
    longitude = None
    matches = GEO_RE.findall(html)

    if matches:
        latitude, longitude = matches[0]

    return (latitude, longitude)


# TODO: Falta considerar videos. Ejemplo:
# http://elobservador.com.uy/noticia/215423/la-desigualdad-disminuyo-en-america-latina/
def mk_media(element):
    try:
        url = element.select('*/img/@src').extract()[0]
    except IndexError:
        url = None

    # Contains copyright symbol
    author = element.select('div[@class="copyright"]/text()').extract()

    if len(author) == 1:
        author = author[0][2:]
    elif len(author) > 1:
        print author
        import ipdb; ipdb.set_trace()

    if not url:
        print url
        print author
        import ipdb; ipdb.set_trace()

    media = Media(url=url, photographer=author)

    return media


def parse_author(div):
    author = div.select('b/text()').extract()[0]
    if author == '+ ':
        return ()

    return (author[2:],)


def parse_body(elements):
    body = ''

    for element in elements:
        el_class = element.select('@class').extract()
        el_id = element.select('@id').extract()
        if el_class in ([], ['MsoNormal'], ['embed']) and el_id == []:
            content = element.extract()
            if 'googleFillSlot' not in content:
                body += to_markup(content)

    return body.strip()


# Example match: u' - 28.08.2013,  15:24 hs\n    -\xa0ACTUALIZADO 21:07\n    '
def get_date(matches):
    for match in matches:
        match = match.strip()
        if match != '' and match.startswith('- '):
            timestamp = match[2:].split('\n')[0]

            try:
                date = datetime.strptime(timestamp, '%d.%m.%Y,  %H:%M hs')
            except ValueError:
                # '20.12.2011,   hs  09:30'
                hour = match.split('ACTUALIZADO')[-1]
                timestamp = ' '.join((timestamp, hour))
                date = datetime.strptime(timestamp, u'%d.%m.%Y,   hs  %H:%M')

            return date

    import ipdb; ipdb.set_trace()
