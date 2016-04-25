import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'smartooz.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

###################################################################################################



@app.route('/accept/<int:article_id>', methods=['GET'])
def accept_article(article_id):
    flash('Invalid action. Sorry, only an admin can do this.')
    return redirect(url_for('show_articles'))


@app.route('/disable/<int:article_id>', methods=['GET'])
def disable_article(article_id):
    flash('Invalid action. Sorry, only an admin can do this.')
    return redirect(url_for('show_articles'))


@app.route('/')
def show_articles():
    if not session.get('user_id'):
        flash('Please login or register to access our services.')
        return redirect(url_for('register'))
    db = get_db()
    flag = ''
    cur = db.execute('select * from articles where id_user=?',
                            [session.get('user_id')])
    flag = "coucou"
    articles = cur.fetchall()
    return render_template('show_articles.html', articles=articles, flag=flag)


@app.route('/add', methods=['POST'])
def add_article():
    if not session.get('user_id'):
        flash('Please login or register to access our services.')
        return redirect(url_for('register'))

    try:
        price = int(request.form['price'])
        if price < 0:
            abort(400)
        db = get_db()
        db.execute('insert into articles (name, description, price, is_accepted, is_read, photo, id_user) values (?, ?, ?, 0, 0, ?, ?)',
                   [request.form['name'], request.form['description'], price, request.form['photo'], session.get('user_id')])
        db.commit()
    except ValueError:
        abort(400)
    flash('New ad was successfully posted. An admin will check it as soon as possible !')
    return redirect(url_for('show_articles'))


@app.route('/update/<int:article_id>', methods=['POST', 'GET'])
def update_article(article_id):
    if not session.get('user_id'):
        flash('Please login or register to access our services.')
        return redirect(url_for('register'))
    
    db = get_db()
    if request.method == 'POST':
        try:
            price = int(request.form['price'])
            if price < 0:
                abort(400)
            db.execute('UPDATE articles SET name=?, description=?, price=?, photo=? WHERE id=?',
                   [request.form['name'], request.form['description'], price, request.form['photo'], article_id])
            db.commit()
            flash('Ad was successfully updated.')
        except ValueError:
            abort(400)
    else:
        cur = db.execute('SELECT * FROM articles WHERE id=?', [article_id])
        article = cur.fetchone()
        if not article:
            abort(404)
        return render_template('edit.html', article=article)

    return redirect(url_for('show_articles'))


@app.route('/login', methods=['POST'])
def login():
    # curl -X POST -d '{"password":"hugo","username":"papin2"}' http://127.0.0.1:5000/login --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie
    import hashlib, json
    request_json = request.get_json()
    password = hashlib.sha256(request_json.get('password', 'bla').encode('utf-8')).hexdigest()
    db = get_db()
    cur = db.execute('select * from users where password=? and username=?',
                        [password, request_json.get('username', 'bla')])
    user = cur.fetchone()
    resp = {
        'status': 'KO'
    }
    if user != None:
        session['user_id'] = user['id']
        resp['status'] = 'OK'
        resp['username'] = user['username']
        resp['email'] = user['email']
    return render_template('response.json', response=json.dumps(resp))


@app.route('/register', methods=['POST'])
def register():
    import hashlib, json
    request_json = request.get_json()
    password = hashlib.sha256(request_json.get('password').encode('utf-8')).hexdigest()
    username = request_json.get('username')
    email = request_json.get('email')
    resp = {
        'status': 'KO'
    }

    if not (request_json.get('password') and username and email):
        resp['error'] = 'You didn\'t fill all the fields.'
    else:
        db = get_db()
        cur = db.execute('select * from users where username=?', [username])
        user = cur.fetchone()
        if user == None:
            db.execute('insert into USERS (email, password, username) values (?, ?, ?)',
                            [email, password, username])
            db.commit()
            cur = db.execute('select * from users where password=? and username=?',
                        [password, request_json.get('username', 'bla')])
            user = cur.fetchone()
            if user != None:
                session['user_id'] = user['id']
                resp['status'] = 'OK'
                resp['username'] = user['username']
                resp['email'] = user['email']
        else:
            resp['error'] = 'Sorry, username already exists.'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    resp = {
        'status': 'OK'
    }
    return render_template('response.json', response=json.dumps(resp))

