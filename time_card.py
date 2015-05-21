#!/usr/bin/python
# Overview here

import sqlite3, flask, hashlib, datetime, functools, contextlib, user_maker

# This constant determines the logout time limit
time_limit = 300 # 5 minutes

app = flask.Flask(__name__)

app.secret_key = b'w\xec\x90\xfd\xac\x847k(\x16\x96\xb9"\x95\xdf9\x10v\\\xf0\xcd\xfe\xa2k'

# Authenticating session

def requires_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in flask.session:
            flask.flash('You have been logged out due to inactivity.')
            return flask.redirect(flask.url_for('login'))
        return f(*args, **kwargs)
    return decorated


def requires_admin(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in flask.session:
            flask.flash('You have been logged out due to inactivity.')
            return flask.redirect(flask.url_for('login'))
        if not is_admin(flask.session['username']):
            flask.flash('You don\'t have permission to view that page.')
            return flask.redirect(flask.url_for('buttons'))
        return f(*args, **kwargs)
    return decorated

# Loading the database

@app.before_request
def before_request():
    flask.g.db = sqlite3.connect('db.db')
    c = flask.g.db.cursor()
    c.execute('PRAGMA foreign_keys = ON')

@app.teardown_request
def teardown_request(exception):
    db = getattr(flask.g, 'db', None)
    if db is not None:
        db.close()

def init_db():
    with contextlib.closing(sqlite3.connect('db.db')) as db:
        with app.open_resource('db_creation.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Login check function

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    # This small script ensures people do not stay logged in
    app.permanent_session_lifetime = datetime.timedelta(seconds = time_limit)

    if flask.request.method == 'POST':
        c = flask.g.db.cursor()
        input_usr = flask.request.form['username']
        input_pw = flask.request.form['password']
        hashed_pw = hashlib.md5(input_usr.encode('utf-8') + input_pw.encode('utf-8')).hexdigest()
        c.execute('select username from users where username=? and password=?', (input_usr, hashed_pw))
        if c.fetchone() is None:
            error = 'Invalid username or password.'
        else:
            flask.session.permanent = True
            flask.session['username'] = input_usr
            flask.flash('You are now logged in.')
            return flask.redirect(flask.url_for('buttons'))
    return flask.render_template('login.html', error=error)

@app.route('/logout')
def logout():
    flask.flash('You have been logged out.')
    flask.session.pop('username', None)
    return flask.redirect(flask.url_for('login'))

@app.route('/buttons', methods=['GET', 'POST'])
@requires_auth
def buttons():
    if flask.request.method =='POST':
        if 'checkin' in flask.request.form:
            checked_value = write_checkin(flask.session['username'])
            if checked_value is None:
                flask.flash('There was some write error.')
            else:
                flask.flash('You have been checked in.')
                flask.flash('Remember to check out at the end of the day!')
                flask.session.pop('username', None)
                return flask.redirect(flask.url_for('login'))
        if 'checkout' in flask.request.form:
            checked_value = write_checkout(flask.session['username'])
            if checked_value is None:
                flask.flash('There was some write error.')
            else:
                flask.flash('You have been checked out.')
                flask.flash('Enjoy the rest of your day!')
                flask.session.pop('username', None)
                return flask.redirect(flask.url_for('login'))

    return flask.render_template('buttons.html', checked_in=checked_in(flask.session['username']), is_admin=is_admin(flask.session['username']))

@app.route('/add_user', methods=['GET', 'POST'])
@requires_admin
def add_user():
    if flask.request.method == 'POST':
        user = flask.request.form['username']
        pass1 = flask.request.form['password']
        pass2 = flask.request.form['password_try']
        admin = flask.request.form['checkbox']
        print(admin)
    return flask.render_template('add_user.html', is_admin=is_admin(flask.session['username'])) 

def is_admin(in_username):
    c = flask.g.db.cursor()
    c.execute('select admin from users where username=?', (in_username,))
    ret = c.fetchone()
    if (ret is None) or (ret[0]==0):
        print('returned f')
        return False
    else:
        return True

def write_checkin(in_username):
    c = flask.g.db.cursor()
    c.execute("insert into history ('userid', 'checkin') select id, ? from users where username=?", (datetime.datetime.now(), in_username))
    flask.g.db.commit()
    return c.lastrowid

def checked_in(in_username):
    c = flask.g.db.cursor()
    c.execute('select username, checkin from users, history where users.username=? and users.id=history.userid and checkout is null', (in_username,))
    ret = c.fetchone()
    print(ret)
    if ret is None: 
        return False
    recorded_time = datetime.datetime.strptime(ret[1], '%Y-%m-%d %H:%M:%S.%f')   
    if recorded_time.date() == datetime.date.today():
        return True
    else:
        write_checkout(in_username, datetime.datetime.combine(recorded_time.date(), datetime.datetime.time(23, 59, 59)))

    return True

def write_checkout(in_username, date = None):
    c = flask.g.db.cursor()
    if date == None:
        date = datetime.datetime.now()
    c.execute("update history set checkout=? where checkout is null and userid=(select id from users where username=?)", (date, in_username))
    flask.g.db.commit()
    return c.rowcount



if __name__ == '__main__':
    app.run(debug = True)
