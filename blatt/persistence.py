# -*- coding: utf-8 -*-
import os

from sqlalchemy import (create_engine, Column, Integer, String, Text, DateTime,
                        Table)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

dirname = os.path.dirname(__file__)

engine = create_engine('sqlite:///' + dirname + '/../blatt.db')

Base = declarative_base()
Session = sessionmaker(bind=engine)

session = Session()


class Publication(Base):
    __tablename__ = 'publications'

    pk = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False)
    logo = Column(String, nullable=False, unique=True)
    url = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return "<Publication('%s')>" % self.name


publications_sections = Table('publications_sections', Base.metadata,
    Column('publication_pk', Integer, ForeignKey('publications.pk')),
    Column('section_pk', Integer, ForeignKey('sections.pk'))
)


class Section(Base):
    __tablename__ = 'sections'

    pk = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String)

    publications = relationship('Publication', secondary=publications_sections,
                          backref='sections')

    def __repr__(self):
        return "<Section('%s')>" % self.name


class Journalist(Base):
    __tablename__ = 'journalists'

    pk = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String)

    def __repr__(self):
        return "<Journalist('%s')>" % self.name


journalists_articles = Table('journalists_articles', Base.metadata,
    Column('journalist_pk', Integer, ForeignKey('journalists.pk')),
    Column('article_pk', Integer, ForeignKey('articles.pk'))
)


class Article(Base):
    __tablename__ = 'articles'

    pk = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    deck = Column(String)
    lead = Column(String)
    body = Column(Text)
    url = Column(String, nullable=False, unique=True)
    latitude = Column(String)
    longitude = Column(String)
    publication_date = Column(DateTime)
    publication_pk = Column(Integer, ForeignKey('publications.pk'))
    section_pk = Column(Integer, ForeignKey('sections.pk'))

    publication = relationship('Publication',
                               backref=backref('articles',
                                               order_by=publication_date))
    section = relationship('Section',
                           backref=backref('articles',
                                           order_by=publication_date))
    authors = relationship('Journalist', secondary=journalists_articles,
                          backref='articles')

    def __repr__(self):
        return "<Article('%s')>" % self.title


class Photographer(Base):
    __tablename__ = 'photographers'

    pk = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String)

    def __repr__(self):
        return "<Photographer('%s')>" % self.name


class Media(Base):
    __tablename__ = 'medias'

    pk = Column(Integer, primary_key=True)
    url = Column(String, nullable=False, unique=True)
    caption = Column(String)
    article_pk = Column(Integer, ForeignKey('articles.pk'))
    photographer_pk = Column(Integer, ForeignKey('photographers.pk'))

    article = relationship('Article', backref=backref('medias', order_by=pk))
    photographer = relationship('Photographer',
                                backref=backref('photos', order_by=pk))
