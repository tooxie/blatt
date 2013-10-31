# -*- coding: utf-8 -*-
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from blatt.persistence import (Article, Journalist, Base, engine, Journalist,
                               Media, Photographer, Publication, Section,
                               session)
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from slugify import slugify

Base.metadata.create_all(engine)

def get_publication(name=None, logo=None, url=None):
    if get_publication._publication or (not name or not url):
        return get_publication._publication

    slug = slugify(name)

    try:
        _publication = session.query(Publication).filter_by(slug=slug).one()
    except NoResultFound, e:
        _publication = Publication(name=name, slug=slug, logo=logo, url=url)

        session.add(_publication)
        session.commit()
    except MultipleResultsFound, e:
        import ipdb; ipdb.set_trace()

    get_publication._publication = _publication

    return _publication
get_publication._publication = None


def get_journalist(name):
    return get_something(name, Journalist)


def get_photographer(name):
    return get_something(name, Photographer)


def get_section(name):
    if not name:
        return None

    def enrich(section):
        publication = get_publication()

        if not publication:
            return None

        if publication not in section.publications:
            section.publications.append(publication)

    return get_something(name, Section, enrich)


def get_something(name, Model, enricher=None):
    if not name:
        return None

    try:
        something = session.query(Model).filter_by(slug=slugify(name)).one()
    except NoResultFound, e:
        something = Model(name=name, slug=slugify(name))

        if enricher:
            enricher(something)

        session.add(something)
        session.commit()
    except MultipleResultsFound, e:
        import ipdb; ipdb.set_trace()

    return something


class BlattPipeline(object):
    def process_item(self, item, spider):
        publication = get_publication(spider.publication_name, spider.logo,
                                      spider.url)
        try:
            article = session.query(Article).filter_by(url=item['url']).one()
        except NoResultFound:
            article = Article()
        except MultipleResultsFound, e:
            import ipdb; ipdb.set_trace()

        article.title = item['title']
        article.deck = item.get('deck')
        article.lead = item.get('lead')
        article.body = item['body']
        article.url = item['url']
        article.authors = [get_journalist(author) \
                           for author in item.get('authors', [])]
        article.latitude = item.get('latitude')
        article.longitude = item.get('longitude')
        article.publication_date = item['date']
        article.publication = publication
        article.section = get_section(item.get('section'))

        for m in item.get('media', []):
            try:
                media = session.query(Media).filter_by(url=m['url']).one()
            except NoResultFound:
                media = Media()
            except MultipleResultsFound, e:
                import ipdb; ipdb.set_trace()

            media.url = m['url']
            media.caption = m.get('caption')
            media.photographer = get_photographer(m.get('photographer'))
            media.article = article

            session.add(media)

        session.add(article)
        try:
            session.commit()
        except Exception, e:
            import ipdb; ipdb.set_trace()

        return item
