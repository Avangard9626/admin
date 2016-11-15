# coding=utf-8
import ConfigParser

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.engine.url import URL

Base = declarative_base()
m = Base.metadata
Config = ConfigParser.ConfigParser()
Config.read('vars.ini')
db_vars = dict(Config.items('Database'))


# Подключение к БД
def db_connect():
    return create_engine(URL(**db_vars))
engine = db_connect()
Session = sessionmaker()
Session.configure(bind=engine)


def create_all(engine):
    Base.metadata.create_all(engine)
    session = Session()
    paymenttypes = [
        Paymenttype('coins'),
        Paymenttype('eggs'),
        Paymenttype('voices')
    ]
    languages = [
        Language('Русский', 'rus'),
        Language('English', 'eng')
    ]
    zodiacs = [
        Zodiac('Овен'),
        Zodiac('Телец'),
        Zodiac('Близнецы'),
        Zodiac('Рак'),
        Zodiac('Лев'),
        Zodiac('Дева'),
        Zodiac('Весы'),
        Zodiac('Скорпион'),
        Zodiac('Стрелец'),
        Zodiac('Козерог'),
        Zodiac('Водолей'),
        Zodiac('Рыбы')
    ]
    products = [
        Product(1, 'Базовый набор', 'base_set', '1', '/', '0', '0', False, '05 Dec 2000')
    ]
    producttype = [
        ProductType('Цитаты')
    ]
    session.add_all(paymenttypes)
    session.add_all(languages)
    session.add_all(zodiacs)
    session.add_all(products)
    session.add_all(producttype)
    session.commit()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer, unique=True)
    coincurr = Column(Integer)
    eggcurr = Column(Integer)
    current_egg_skin = Column(Integer)
    zodiac_id = Column(Integer, ForeignKey('zodiac.id'))
    readed_quotes = Column(postgresql.ARRAY(Integer))
    readed_words = Column(postgresql.ARRAY(Integer))
    purchases = Column(postgresql.ARRAY(Integer), default={})
    purchases_rel = relationship("Purchase")
    is_del = Column(Boolean, default=False)

    def __init__(self, vk_id, coincurr, eggcurr, current_egg_skin, zodiac_id, purchases):
        self.vk_id = vk_id
        self.coincurr = coincurr
        self.eggcurr = eggcurr
        self.current_egg_skin = current_egg_skin
        self.zodiac_id = zodiac_id
        self.purchases = purchases


class Purchase(Base):
    __tablename__ = 'purchase'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer, ForeignKey('user.vk_id'))
    date = Column(DateTime)
    price = Column(Float)
    product_id = Column(Integer, ForeignKey('product.id'))
    is_del = Column(Boolean, default=False)

    def __init__(self, user_id, date, price, product_id):
        self.user_id = user_id
        self.date = date
        self.price = price
        self.product_id = product_id


class Statistic(Base):
    __tablename__ = 'statistic'

    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))
    gametype_id = Column(Integer, ForeignKey('gametype.id'))
    is_del = Column(Boolean, default=False)

    def __init__(self, quantity, user_id, gametype_id):
        self.quantity = quantity
        self.user_id = user_id
        self.gametype_id = gametype_id


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    title = Column(String(50))
    skin_id = Column(Integer)
    img = Column(String(128))
    product_type_id = Column(Integer, ForeignKey('producttype.id'))
    atlas = Column(Integer, ForeignKey('atlas.id'))
    payment_type = Column(Integer, ForeignKey('paymenttype.id'))
    price = Column(Integer, default=0)
    price_old = Column(Float)
    is_new = Column(Boolean)
    timer_end = Column(DateTime)
    is_del = Column(Boolean, default=False)

    def __init__(self, product_type_id, name, title, skin_id, atlas_path, price, price_old, is_new, timer_end):
        self.product_type_id = product_type_id
        self.name = name
        self.title = title
        self.skin_id = skin_id
        self.atlas_path = atlas_path
        self.price = price
        self.price_old = price_old
        self.is_new = is_new
        self.timer_end = timer_end


class ProductType(Base):
    __tablename__ = 'producttype'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32))

    def __init__(self, name):
        self.name = name


class Paymenttype(Base):
    __tablename__ = 'paymenttype'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32))

    def __init__(self, name):
        self.name = name


class Gametype(Base):
    __tablename__ = 'gametype'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    is_del = Column(Boolean, default=False)

    def __init__(self, name):
        self.name = name


class Zodiac(Base):
    __tablename__ = 'zodiac'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    is_del = Column(Boolean, default=False)

    def __init__(self, name):
        self.name = name


class Horoscope(Base):
    __tablename__ = 'horoscope'

    id = Column(Integer, primary_key=True, autoincrement=True)
    img_path = Column(String(255))
    zodiac_id = Column(Integer, ForeignKey('zodiac.id'))
    is_del = Column(Boolean, default=False)

    def __init__(self, img_path, zodiac_id):
        self.img_path = img_path
        self.zodiac_id = zodiac_id


class Atlas(Base):
    __tablename__ = 'atlas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    atlas = Column(String(128))
    atlas_xml = Column(String(128))
    is_del = Column(Boolean, default=False)

    def __init__(self, atlas, atlas_xml):
        self.atlas = atlas
        self.atlas_xml = atlas_xml


class Quote(Base):
    __tablename__ = 'quote'

    id = Column(Integer, primary_key=True, autoincrement=True)
    background = Column(Integer, ForeignKey('background.id'))
    topic = Column(String(32))
    text = Column(String(128))
    is_del = Column(Boolean, default=False)

    def __init__(self, background, topic, text):
        self.background = background
        self.topic = topic
        self.text = text


class Background(Base):
    __tablename__ = 'background'

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(128))


class Word(Base):
    __tablename__ = 'word'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    language_id = Column(Integer, ForeignKey('language.id'))
    word_id = Column(String(256))
    is_del = Column(Boolean, default=False)

    def __init__(self, name, language_id, word_id):
        self.name = name
        self.language_id = language_id
        self.word_id = word_id


class Language(Base):
    __tablename__ = 'language'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    short_name = Column(String(3))
    is_del = Column(Boolean, default=False)

    def __init__(self, name, short_name):
        self.name = name
        self.short_name = short_name


class Flash(Base):
    __tablename__ = 'flash'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    path = Column(String(128))
    version = Column(String(20))
    date = Column(DateTime)
    is_use = Column(Boolean)
    is_del = Column(Boolean, default=False)

    def __init__(self, name, path, version, date, is_use):
        self.name = name
        self.path = path
        self.version = version
        self.date = date
        self.is_use = is_use
