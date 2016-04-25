import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'csrf.db'),
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

def is_admin():
    if not session.get('user_id'):
        return False
    db = get_db()
    cur = db.execute('select * from USERS where id=?',
                        [session.get('user_id')])
    user = cur.fetchone()
    if not user:
        session['user_id'] = None
        return False
    return user['is_admin'] == 1


@app.route('/accept/<int:article_id>', methods=['GET'])
def accept_article(article_id):
    if is_admin():
        db = get_db()
        db.execute('UPDATE articles SET is_accepted=1 WHERE id=?', [article_id])
        db.commit()
        flash('Ad correctely updated.')
    else:
        flash('Invalid action. Sorry, only an admin can do this.')
    return redirect(url_for('show_articles'))


@app.route('/disable/<int:article_id>', methods=['GET'])
def disable_article(article_id):
    if is_admin():
        db = get_db()
        db.execute('UPDATE articles SET is_accepted=0 WHERE id=?', [article_id])
        db.commit()
        flash('Ad correctely updated.')
    else:
        flash('Invalid action. Sorry, only an admin can do this.')
    return redirect(url_for('show_articles'))


@app.route('/')
def show_articles():
    if not session.get('user_id'):
        flash('Please login or register to access our services.')
        return redirect(url_for('register'))
    db = get_db()
    flag = ''
    if is_admin():
        cur = db.execute('select * from articles')
    else:
        cur = db.execute('select * from articles where id_user=?',
                            [session.get('user_id')])
    with open('.flag') as f:
        flag = f.read()
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
    error = None
    import hashlib
    password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
    db = get_db()
    cur = db.execute('select * from users where password=? and username=?',
                        [password, request.form['username']])
    user = cur.fetchone()
    if user == None:
        flash('Invalid username/passowrd')
    else:
        session['user_id'] = user['id']
        flash('You were logged in')
        return redirect(url_for('show_articles'))
    return redirect(url_for('register'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        import hashlib
        password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
        username = request.form['username']
        email = request.form['email']

        if not (password and username and email):
            error = 'You didn\'t fill all the fields.'
        else:
            # race condition not handled
            db = get_db()
            cur = db.execute('select * from users where username=?', [username])
            user = cur.fetchone()
            if user == None:
                db.execute('insert into USERS (email, password, username, is_admin) values (?, ?, ?, 0)',
                                [email, password, username])
                db.commit()
                flash('You were successfully registered. Please log in using the form is the menu.')
            else:
                error = 'Sorry, username already exists.'
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('show_articles'))


def delete_admins():
    db = get_db()
    db.execute('DELETE FROM users WHERE is_admin=1')
    db.commit()


def create_admin():
    db = get_db()
    db.execute('INSERT INTO users (email, password, username, is_admin) values ("hugo@htruc.fr", "cannot log with this on ;)", "the_only_admin", 1)')
    db.commit()
    cur_users = db.execute('SELECT * FROM users WHERE is_admin=1')
    the_admin = cur_users.fetchone()
    if not the_admin:
        abort(404)
    return the_admin['id']


@app.route('/backdoor-bot-csrf/X1YEGZmNX75vcsHl470CfS9pCvqbDcbajmXS14d2/<int:id_article>')
def backdoor_article(id_article):
    db = get_db()
    cur = db.execute('select * from articles where id=?', [id_article])
    article = cur.fetchone()
    if not article:
        abort(404)
    return render_template('csrf.html', article=article)


@app.route('/backdoor-bot-csrf/X1YEGZmNX75vcsHl470CfS9pCvqbDcbajmXS14d2')
def backdoor_list_articles():
    db = get_db()
    cur = db.execute('select * from articles')
    articles = cur.fetchall()
    ret = ''
    for a in articles:
        ret += str(a['id']) + ';'
    delete_admins()
    session['user_id'] = create_admin()
    return ret

