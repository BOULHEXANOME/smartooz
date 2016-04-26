import os, json
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'smartooz.db'),
    DEBUG=True,
    SECRET_KEY='development key boulhexanome',
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

def fetchone_custom(cur):
    list_sqlite = cur.fetchone()
    list_ret = []
    for item in list_sqlite:
        list_ret.append(item)
    return list_ret


def fetchall_custom(cur):
    list_sqlite = cur.fetchall()
    list_ret = []
    for item in list_sqlite:
        item_custom = []
        for i in item:
            item_custom.append(i)
        list_ret.append(item_custom)
    return list_ret

def get_user(user_id):
    if user_id is None:
        return None
    db = get_db()
    cur = db.execute('SELECT * FROM users WHERE id=?', [user_id])
    return fetchone_custom(cur)


def get_place(place_id):
    if place_id is None:
        return None
    db = get_db()
    cur = db.execute('SELECT * FROM places WHERE id=?', [place_id])
    ret = fetchone_custom(cur)
    return ret


@app.route('/add-place', methods=['POST'])
def add_place():
    # curl -X POST -d '{"latitude":45.75,"longitude":4.8,"address":"ta mere","openning_hours":"tout le temps","name":"tour papine","description":"flemme","keywords":["sfm", "HOHO"]}' http://127.0.0.1:5000/add-place --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    request_json = request.get_json()
    try:
        if float(request_json.get('latitude')) < 45.7 or float(request_json.get('latitude')) > 45.8 or float(request_json.get('longitude'))<4.7 or float(request_json.get('longitude'))>5.0:
            resp['error'] = 'Note between 0 and 5.'
            return render_template('response.json', response=json.dumps(resp))
        if not request_json.get('keywords'):
            resp['error'] = 'No keywords given.'
            return render_template('response.json', response=json.dumps(resp))

        db = get_db()
        db.execute('INSERT INTO places (lat, long, address, phone, website, openning_hours, name, description, id_user, note_5, nb_vote) values (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)',
                   [float(request_json.get('latitude')), 
                   float(request_json.get('longitude')), 
                   request_json.get('address'), 
                   request_json.get('phone'), 
                   request_json.get('website'), 
                   request_json.get('openning_hours'), 
                   request_json.get('name'), 
                   request_json.get('description'), 
                   session.get('user_id')])
        db.commit()
        cur = db.execute('SELECT * FROM places WHERE lat=? AND long=?', [float(request_json.get('latitude')), float(request_json.get('longitude'))])
        place_inserted = cur.fetchone()
        for k in request_json.get('keywords'):
            k = k.upper()
            cur = db.execute('SELECT * FROM keywords where name=?', [k])
            keyword = cur.fetchone()
            if not keyword:
                db.execute('INSERT INTO keywords (name) values (?)', [k])
                db.commit()
                cur = db.execute('SELECT * FROM keywords where name=?', [k])
                keyword = cur.fetchone()
            # on peut inserer la relation place/keyword
            db.execute('INSERT INTO place_keywords (id_place_or_circuit, id_keyword) values (?, ?)', [place_inserted['id'], keyword['id']])
            db.commit()
        resp['status'] = 'OK'

    except:
        resp['error'] = 'An error occured while inserting place.'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/delete-place/', methods=['POST'])
def delete_place():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    request_json = request.get_json()
    user = get_user(session['user_id'])
    place = get_place(request_json.get('place_id', '-1'))
    if not user:
        resp['error'] = 'User not found sorry.'
        return render_template('response.json', response=json.dumps(resp))
    if not place:
        resp['error'] = 'User not found sorry.'
        return render_template('response.json', response=json.dumps(resp))
    if place['id_user'] != user['id']:
        resp['error'] = 'You are not allowed to access or modify this ressource.'
        return render_template('response.json', response=json.dumps(resp))

    db = get_db()
    db.execute('DELETE FROM places WHERE id=?', [place['id']])
    db.execute('DELETE FROM place_keywords WHERE id_place_or_circuit=?', [place['id']])
    db.commit()
    resp['status'] = 'OK'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/get-places', methods=['GET'])
def get_places():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    try:
        db = get_db()
        cur = db.execute('SELECT * FROM places')
        list_places = fetchall_custom(cur)
        resp['status'] = 'OK'
        resp['list_places'] = list_places
    except:
        resp['error'] = 'An error occured while inserting place.'
    return render_template('response.json', response=json.dumps(resp))
    
    
@app.route('/get-place-coord/<float:lat>,<float:longitude>', methods=['GET'])
def get_place_coord(lat,longitude):
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    try:
        db = get_db()
        cur = db.execute('SELECT * FROM places WHERE lat=? AND long=?', [lat,longitude])
        place = fetchone_custom(cur)
        resp['status'] = 'OK'
        resp['place'] = place
    except:
        resp['error'] = 'An error occured while inserting place.'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/get-place-id/<int:place_id>', methods=['GET'])
def get_place_id(place_id):
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    try:
        place = get_place(place_id)
        resp['status'] = 'OK'
        resp['place'] = place
    except:
        resp['error'] = 'An error occured while getting place.'
    return render_template('response.json', response=json.dumps(resp))
    

@app.route('/get-places-keyword/<int:keyword_id>', methods=['GET'])
def get_places_keyword(keyword_id):
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    try:
        db=get_db()
        list_places = db.execute(('SELECT * FROM places WHERE id IN (SELECT id_place_or_circuit FROM place_keywords WHERE id_keyword=?))', [keyword_id])
        
        places = fetchall_custom(list_places)
        resp['status'] = 'OK'
        resp['places'] = places
    except:
        resp['error'] = 'An error occured while inserting place.'
    return render_template('response.json', response=json.dumps(resp))
    


@app.route('/update-place/<int:place_id>', methods=['POST'])
def update_place(place_id):
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    user = get_user(session['user_id'])
    place = get_place(place_id)
    if not user:
        resp['error'] = 'User not found sorry.'
        return render_template('response.json', response=json.dumps(resp))
    if not place:
        resp['error'] = 'User not found sorry.'
        return render_template('response.json', response=json.dumps(resp))
    if place['id_user'] != user['id']:
        resp['error'] = 'You are not allowed to access or modify this ressource.'
        return render_template('response.json', response=json.dumps(resp))
    
    try:
        if float(request_json.get('note', '0')) < 0 or float(request_json.get('note', '0')) > 5:
            resp['error'] = 'Note between 0 and 5.'
            return render_template('response.json', response=json.dumps(resp))
        if float(request_json.get('latitude')) < 45.7 or float(request_json.get('latitude')) > 45.8 or float(request_json.get('longitude'))<4.7 or float(request_json.get('longitude'))>5.0:
            resp['error'] = 'Note between 0 and 5.'
            return render_template('response.json', response=json.dumps(resp))    
        if not request_json.get('keywords'):
            resp['error'] = 'No keywords given.'
            return render_template('response.json', response=json.dumps(resp))   

        db = get_db()
        db.execute('UPDATE places SET lat=?, long=?, address=?, phone=?, website=?, openning_hours=?, name=?, description=? WHERE id=?',
                   [float(request_json.get('latitude')), 
                   float(request_json.get('longitude')), 
                   request_json.get('address'), 
                   request_json.get('phone'), 
                   request_json.get('website'), 
                   request_json.get('openning_hours'), 
                   request_json.get('name'), 
                   request_json.get('description'),
                   user['id']])
        db.commit()
        place = get_place(place_id)
        db.execute('DELETE FROM place_keywords WHERE id_place_or_circuit=?', [place['id']])
        db.commit()
        for k in request_json.get('keywords'):
            k = k.upper()
            cur = db.execute('SELECT * FROM keywords where name=?', [k])
            keyword = cur.fetchone()
            if not keyword:
                db = get_db()
                db.execute('INSERT INTO keywords (name) values (?)', [k])
                db.commit()
                cur = db.execute('SELECT * FROM keywords where name=?', [k])
                keyword = cur.fetchone()
            # on peut inserer la relation place/keyword
            db.execute('INSERT INTO place_keywords (id_place_or_circuit, id_keyword) values (?, ?)', [place_inserted['id'], keyword['id']])
            db.commit()
        
        resp['status'] = 'OK'
    except:
        resp['error'] = 'An error occured while inserting place.'

    return render_template('response.json', response=json.dumps(resp))


@app.route('/login', methods=['POST'])
def login():
    # curl -X POST -d '{"password":"hugo","username":"papin2"}' http://127.0.0.1:5000/login --header "Content-Type:application/json" -c /tmp/cookie -b /tmp/cookie
    import hashlib
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
    import hashlib
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
        cur = db.execute('SELECT * FROM users where username=?', [username])
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

    
@app.route('/delete_user', methods=['POST'])
def delete_user(user_id):
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    request_json = request.get_json()
    user = get_user(session['user_id'])
    user_to_delete = get_user(request_json.get('user_id', '-1'))
    if not user:
        resp['error'] = 'User not found sorry.'
        return render_template('response.json', response=json.dumps(resp))
    else:
        db = get_db()
        db.execute('DELETE FROM users WHERE id=?', [user['id']])
        db.commit()
        resp['status'] = 'OK'
        return render_template('response.json', response=json.dumps(resp))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    resp = {
        'status': 'OK'
    }
    return render_template('response.json', response=json.dumps(resp))

