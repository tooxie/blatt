from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///blatt.db')

Base = declarative_base()
Session = sessionmaker(bind=engine)

session = Session()


class Publication(Base):
    __tablename__ = 'publications'

    pk = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)


class Article(Base):
    __tablename__ = 'articles'

    pk = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    deck = Column(String)
    lead = Column(String)
    body = Column(Text)
    url = Column(String, nullable=False, unique=True)
    publication_date = Column(Date)
    publication_pk = Column(Integer, ForeignKey('publications.pk'))

    publication = relationship("Publication", backref=backref('articles',
                                                              order_by=pk))

    def __repr__(self):
        return "<Article('%s')>" % self.title
