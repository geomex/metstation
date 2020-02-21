'''
Description:

by: Joel A. Gongora
date: 12/31/2019
'''

from flask import (Flask, render_template,
                   request, url_for, redirect, flash,
                   session)
from wtforms import (Form, StringField, TextAreaField,
                     PasswordField, validators)
from passlib.hash import sha256_crypt
import psycopg2
import psycopg2.extras
# from flaskext.mysql import MySQL
from os.path import abspath
import os
import sys
from functools import wraps

my_app = Flask(__name__)
my_app.debug = True



if not abspath('../utils/') in sys.path:
    sys.path.append(abspath('../utils/'))
    from myconfig import db_config

IMAGE_FOLDER = os.path.join('/static','images')
my_app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unathorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@my_app.route('/logout', methods=['GET', 'POST'])
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@my_app.route('/')
def index():
    return render_template('home.html')


@my_app.route('/dashboard/')
@is_logged_in
def snotel_dashboard():
    return redirect(url_for('/snotel_dashboard/'))


@my_app.route('/about')
def about():
    nasa_img = os.path.join(
        my_app.config['UPLOAD_FOLDER'], 'nasa_logo.png'
    )
    bsu_img = os.path.join(
        my_app.config['UPLOAD_FOLDER'], 'bsu.png'
    )
    eri_img = os.path.join(
        my_app.config['UPLOAD_FOLDER'], 'eri.png'
    )    
    return render_template(
        'about.html', nasa_img=nasa_img, bsu_img=bsu_img,
        eri_img=eri_img
    )

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('PasswordField', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# ------------- #
# User Register #
# ------------- #
@my_app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        conn = psycopg2.connect(
            host=db_config['host'],
            user=db_config['user'],
            password='',
            dbname=db_config['dbname']
        )
        # Create the Cursor #
        cur = conn.cursor()

        # Execute Query
        cur.execute(
            "INSERT INTO users(name, email, username, password)" +
            " VALUES(%s, %s, %s, %s)", (name, email, username, password)
        )

        conn.commit()

        # Close connection
        cur.close()
        conn.close()

        flash('You are now registered and can log in.', 'success')

        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@my_app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create a Cursor #
        conn = psycopg2.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            dbname=db_config['dbname']
        )
        cur = conn.cursor(
            # Return Dictionary #
            cursor_factory=psycopg2.extras.DictCursor
        )

        # Get User by username
        cur.execute(
            f"SELECT * FROM users WHERE username = '{username}'"
        )
        data = cur.fetchone()
        if data is not None:
            # Get Stored Hash
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Password Passed #
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return render_template('home.html')
            else:
                error = 'Invalid Login'
                return render_template('login.html', error=error)                
                app.logger.info('PASSWORD INCORRECT')
                
            # Close Connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
            

    return render_template('login.html')

@my_app.route('/articles')
def articles():
    # Create a Cursor #
    conn = psycopg2.connect(
        host=db_config['host'],
        user=db_config['user'],
        password='',
        dbname=db_config['dbname']
    )
    cur = conn.cursor()    

    # Get articles
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()

    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)

    # Close connection
    cur.close()

