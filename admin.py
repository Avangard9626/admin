# coding=utf-8
# TODO: change redirect() to redirect(url_for())
import hashlib
import os
import requests
import time
import ConfigParser
import datetime

import collections
import uuid
from functools import wraps, update_wrapper

from flask import Flask, render_template, flash, request, send_from_directory, url_for, make_response
from flask import current_app
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import load_only

from models import Session, Quote, Horoscope, Word, Zodiac, Language, Product, Flash
from werkzeug.utils import secure_filename, redirect

config = ConfigParser.ConfigParser()
app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/img')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 Мб
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
session = Session()
tables = [Quote, Horoscope, Word, Zodiac, Language, Product, Flash]
login_session = []


def upload_img(file):
    # Загрузка изображения и возвращение его имени
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename


def auth_require():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # if request.cookies.get('sid') in login_session:
            ret = f(*args, **kwargs)
            return ret
            # else:
            # return redirect(url_for('login'))

        return wrapped

    return decorator


def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, datetime.timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        # Mfd-X43Vh
        if hashlib.sha1(request.form['password']).hexdigest() == '842392391764c88d8ce2819c5e82b2853dadfbaa' \
                and request.form['login'].lower() == 'eggs_admin00':
            cookie = uuid.uuid1()
            login_session.append(cookie.hex)
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('sid', cookie.hex)
            return resp
        else:
            flash('Логин или пароль не верны')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route("/quit")
@auth_require()
def quit():
    login_session.remove(request.cookies.get('sid'))
    return redirect(url_for('login'))


@app.route("/")
@auth_require()
def index():
    return redirect('quotes')
    return render_template('index.html')


@app.route("/quotes")
@auth_require()
def quotation():
    quotes = []
    topics = []
    for row in session.query(Quote):
        quotes.append({
            'id': row.id,
            'img_path': row.background,
            'is_del': row.is_del,
            'topic': row.topic,
            'text': row.text
        })
    for row in session.query(Product).options(load_only('id', 'name')).filter_by(product_type_id=1):
        topics.append({
            'id': row.id,
            'name': row.name
        })
    print topics
    return render_template('quotes.html', quotes=quotes, topics=topics)


@app.route("/quotes/add", methods=['POST'])
@auth_require()
def quote_add():
    if request.method == "POST":
        json = request.get_json()
        new_quote = Quote(1, session.query(Product).options(load_only('name')).filter_by(
            id=int(json['topic'])).one().name, json['text'])
        session.add(new_quote)
        session.commit()
        return redirect('quotes')
    else:
        return redirect('quotes')


@app.route("/quotes/delete", methods=['POST'])
@auth_require()
def quote_delete():
    if request.method == "POST":
        print request.get_json()
        return redirect('quote')


# TODO: recode for use more 2 languages
@app.route("/words", methods=["GET", "POST"])
@auth_require()
def words():
    if request.method == "POST":
        unique_stamp = int(round(time.time() * 1000))
        new_words = []
        for key, value in dict(request.form).iteritems():
            new_word = Word(value[0], key, unique_stamp)
            new_words.append(new_word)
        session.add_all(new_words)
        session.commit()
        return redirect('words')
    else:
        words = {}
        languages = {}
        n_word = 0
        for instance in session.query(Language).order_by('id'):
            line = {
                instance.id: {
                    'id': instance.id,
                    'name': instance.name,
                    'short_name': instance.name
                }
            }
            languages.update(line)
        for instance in session.query(Word).order_by('id'):
            line = {
                languages.get(instance.language_id).get('name'): {
                    'name': instance.name
                }
            }

            if words.get(instance.word_id) is None:
                new_pair = {
                    instance.word_id: line
                }
                words.update(new_pair)
            elif instance.word_id == n_word:
                words.get(instance.word_id).update(line)
            else:
                n_word += 1
                words.get(instance.word_id).update(line)
        sorted_words = collections.OrderedDict(sorted(words.items()))
        return render_template('addlanguage.html', words=sorted_words, languages=languages)


@app.route("/add_language", methods=['GET', 'POST'])
@auth_require()
def add_language():
    if request.method == 'POST':
        name = request.form['name']
        short_name = request.form['short_name']
        new_language = Language(name, short_name)
        session.add(new_language)
        session.commit()
        flash(u'Язык добавлен')
        return redirect(url_for('words'))
    else:
        return redirect(url_for('words'))


@app.route("/update_word", methods=['GET', 'POST'])
@auth_require()
def update_word():
    if request.method == 'POST':
        for key, group in request.get_json():
            print (key, group)
            for language, word in group:
                print (language, word)
    else:
        redirect(url_for('words'))


@app.route("/horoscope")
@auth_require()
def horoscope():
    data = []
    zodiac = {}
    for instance in session.query(Zodiac):
        line = {
            instance.id: instance.name
        }
        zodiac.update(line)
    for instance in session.query(Horoscope):
        line = {
            'id': instance.id,
            'img_path': instance.img_path,
            'zodiac_id': zodiac.get(instance.zodiac_id)
        }
        data.append(line)
    return render_template('horoscope.html', data=data, zodiac=zodiac)


@app.route("/shop", methods=['GET', 'POST'])
@auth_require()
def shop():
    data = []
    if request.method == "POST":
        f = request.files['file']
        filename = upload_img(f)
        new_product = Product(request.form['name'], request.form['title'], filename, request.form['price_eggs'],
                              request.form['price_coins'], request.form['price_voices'], request.form['price_old'],
                              request.form['new'], request.form['timer'])
        session.add(new_product)
        session.commit()
        return redirect('shop')
    else:
        for instance in session.query(Product):
            line = {
                'id': instance.id,
                'name': instance.name,
                'title': instance.title,
                'price_eggs': instance.price_eggs,
                'price_coins': instance.price_coins,
                'price_voices': instance.price_voices,
                'price_old': instance.price_old,
                'new': instance.is_new,
                'timer': instance.timer_end,
                'img': instance.img_addr,
                'is_del': instance.is_del
            }
            data.append(line)
        return render_template('shop.html', data=data)


@app.route("/vars", methods=['GET', 'POST'])
@auth_require()
@crossdomain("*")
def vars():
    if request.method == 'POST':
        configfile = open(os.path.join(os.getcwd(), 'vars.ini'), 'wb')
        print request.get_json()
        for section, key_val in request.get_json().iteritems():
            for key, value in key_val.iteritems():
                config.set(section, key, value)
        config.write(configfile)
        configfile.close()
        requests.post("http://127.0.0.1:8889/update_config")
        return redirect('vars')
    else:
        config.read(os.path.join(os.getcwd(), 'vars.ini'))
        data = {}
        for section in config.sections():
            data.update({section: {}})
            for (key, value) in config.items(section):
                data[section].update({key: value})
        return render_template('vars.html', data=data)


@app.route("/flash", methods=['GET', 'POST'])
@auth_require()
def up_flash():
    if request.method == "POST":
        f = request.files['file']
        filename = request.form['version'] + '_' + secure_filename(f.filename)
        f.save(os.path.join('static/swf', filename))
        session.query(Flash).update({Flash.is_use: False})
        new_flash = Flash(filename, filename, request.form['version'],
                          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), True)
        session.add(new_flash)
        session.commit()
        configfile = open('vars.ini', 'wb')
        config.set('Server', 'swf_path', filename)
        config.write(configfile)
        configfile.close()
        flash(u'Файл загружен')
        requests.post("http://127.0.0.1:8889/update_config")
        return redirect(url_for('up_flash'))
    else:
        data = []
        for instance in session.query(Flash).order_by(Flash.id):
            line = {
                'id': instance.id,
                'name': instance.name,
                'version': instance.version,
                'date': instance.date,
                'is_use': instance.is_use,
            }
            data.append(line)
        # data[0], data[-1] = data[-1], data[0]
        return render_template('flash.html', data=data)


@app.route("/upload_horoscope", methods=['GET', 'POST'])
@auth_require()
def up_horoscope():
    if request.method == "POST":
        f = request.files['file']
        filename = upload_img(f)
        new_horoscope = Horoscope(filename, request.form['zodiac'])
        session.add(new_horoscope)
        session.commit()
        flash('Изображение Загружено')
    return redirect('horoscope')


@app.route("/flash/change/", methods=['GET', 'POST'])
@auth_require()
def flash_change():
    if request.method == "POST":
        session.query(Flash).update({Flash.is_use: False})
        session.query(Flash).filter_by(id=request.form['id']).update({Flash.is_use: True})
        flash = session.query(Flash).filter_by(id=request.form['id']).one()
        session.commit()
        configfile = open('vars.ini', 'wb')
        config.set('Server', 'swf_path', flash.name)
        config.write(configfile)
        configfile.close()
        return redirect(url_for('up_flash'))


@app.route("/add_zodiac", methods=['POST'])
@auth_require()
def add_zodiac():
    if request.method == "POST":
        try:
            new_zodiac = Zodiac(request.form['name'])
            session.add(new_zodiac)
            session.commit()
        except IntegrityError:
            session.rollback()
            flash(u'Знак уже существует')
            return redirect(url_for('horoscope'))
        flash(u'Знак добавлен')
    return redirect('horoscope')


@app.route("/delete_product", methods=['POST'])
@auth_require()
def del_product():
    if request.method == "POST":
        session.query(Product).filter_by(id=request.form['del_id']).update({Product.is_del: True})
        session.commit()
    return redirect('shop')


app.route("/delete_quotation", methods=['POST'])


@auth_require()
def del_quote():
    if request.method == "POST":
        session.query(Quote).filter_by(id=request.form['del_id']).update({Quote.is_del: True})
        session.commit()
    return redirect('quotation')


@app.route("/delete_horoscope", methods=['POST'])
@auth_require()
def del_horoscope():
    if request.method == "POST":
        session.query(Horoscope).filter_by(id=request.form['del_id']).update({Horoscope.is_del: True})
        session.commit()
    return redirect('horoscope')


@app.route('/img/<path:filename>')
@auth_require()
def send_img(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/static/<path:filename>')
@auth_require()
def send_static(filename):
    return send_from_directory(app.static_folder, filename)


if __name__ == "__main__":
    app.secret_key = "BIOdYuvT1MMFGjYX3R4r"
    app.run()
