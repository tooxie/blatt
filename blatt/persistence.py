# -*- coding: utf-8 -*-
import hashlib
import datetime

from sqlalchemy import (create_engine, Column, Integer, String, Text, DateTime,
                        Table)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

from blatt.config import DB_URI

engine = create_engine(DB_URI)

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
                          backref=backref('sections', order_by=name))

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
    scraped_date = Column(DateTime)
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

    article = relationship('Article', backref=backref('media', order_by=pk))
    photographer = relationship('Photographer',
                                backref=backref('photos', order_by=pk))

likes = Table('likes', Base.metadata,
    Column('article_pk', Integer, ForeignKey('articles.pk')),
    Column('user_pk', Integer, ForeignKey('users.pk')),
)


class User(Base):
    __tablename__ = 'users'

    pk = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, nullable=False, unique=True)
    password = Column(String)
    salt = Column(String)

    liked_articles = relationship('Article', secondary=likes,
                                  backref='liked_by')

    def __repr__(self):
        return "<User('%s')>" % self.email

    def set_password(self, password, secret_key):
        self.salt = mk_salt()
        self.password = self.mk_password(password, secret_key)

    def mk_password(self, password, secret_key):
        return mk_password(password, secret_key, self.salt)

    def likes(self, article):
        return article in self.liked_articles

    def get_liked_articles(self, count):
        return self.liked_articles[:count]

    def is_active(self):
        return True

    def get_id(self):
        return self.pk

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

def mk_salt():
    salt = str(datetime.datetime.now())

    return hashlib.md5(salt).hexdigest()

def mk_password(password, secret_key, salt):
    _passwd = '%s#*%s$@%s' % (password, secret_key, salt)

    return hashlib.sha512(_passwd).hexdigest()
