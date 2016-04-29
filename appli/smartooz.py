import os, json
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify
    
app = Flask(__name__)

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'smartooz.db'),
    DEBUG=True,
    SECRET_KEY='development key boulhexanome',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = dict_factory
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


##########################################################################################


##########################################################################################
#                                   USEFULL METHODS
##########################################################################################

LATITUDE_MAX = 45.81
LATITUDE_MIN = 45.71
LONGITUDE_MAX = 4.91
LONGITUDE_MIN = 4.77
USE_API = False


def get_user(user_id):
    if user_id is None:
        return None
    db = get_db()
    cur = db.execute('SELECT * FROM users WHERE id=?', [user_id])
    return cur.fetchone()


def get_place(place_id):
    if place_id is None:
        return None
    db = get_db()
    cur = db.execute('SELECT * FROM places WHERE id=?', [place_id])
    place = cur.fetchone()
    if not place:
        return None
    cur = db.execute(
        'SELECT keywords.name FROM keywords,place_keywords WHERE keywords.id=place_keywords.id_keyword AND id_place=?',
        [place_id])
    place['keywords'] = cur.fetchall()
    return place


def get_circuit(circuit_id):
    if circuit_id is None:
        return None
    db = get_db()
    cur = db.execute('SELECT * FROM circuit WHERE id=?', [circuit_id])
    circuit = cur.fetchone()
    if not circuit:
        return None
    cur = db.execute(
        'SELECT keywords.name FROM keywords,circuit_keywords WHERE keywords.id=circuit_keywords.id_keyword AND id_circuit=?',
        [circuit_id])
    circuit['keywords'] = cur.fetchall()
    cur = db.execute(
        'SELECT id_place FROM circuit_places WHERE id_circuit=?',
        [circuit_id])
    circuit['places'] = cur.fetchall()
    return circuit

 ##########################################################################################
#                                   END USEFULL METHODS
##########################################################################################
#                                        PICTURES
##########################################################################################

@app.route('/upload/<int:circuit_id>,<int:place_id>', methods=['POST'])
def upload_file(circuit_id,place_id):
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))
    try:
        f = request.files['image']
        
        if f and allowed_file(f.filename):
            
            path_user = 'user_' + str(session.get('user_id'))
            path_circuit = 'circuit_' + str(circuit_id)
            name_file = 'place_' + str(place_id)
            
            if not os.path.exists(os.path.join('pictures', path_user, path_circuit)):
                os.makedirs(os.path.join('pictures', path_user, path_circuit))
            
            f.save(os.path.join('.', 'pictures', path_user, path_circuit, name_file))
            
            db = get_db()
            db.execute('INSERT INTO photo_circuit_place_user (id_place, id_circuit, id_user) VALUES (?, ?, ?)', [place_id, circuit_id, session.get('user_id')])
            db.commit()
            resp['status'] = 'OK'

    except ValueError:
        resp['error'] = 'An error occured while uploading file.'
    return render_template('response.json', response=json.dumps(resp))
    
    
@app.route('/download-picture/<int:circuit_id>,<int:place_id>', methods=['GET'])
def download_file(circuit_id, place_id):
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))
    try:
        path_user = 'user_' + str(session.get('user_id'))
        path_circuit = 'circuit_' + str(circuit_id)
        name_file = 'place_' + str(place_id)
            
        file_path = os.path.join('.', 'pictures', path_user, path_circuit, name_file)
        from flask import send_file
        
        file_to_send = send_file(file_path, mimetype='image/jpeg')
        
        return file_to_send;

    except ValueError:
        resp['error'] = 'An error occured while downloading file.'
    return render_template('response.json', response=json.dumps(resp))

        
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

##########################################################################################
#                                   END PICTURES
##########################################################################################
#                                        PLACES
##########################################################################################


@app.route('/add-place', methods=['POST'])
def add_place():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    request_json = request.get_json()
    try:
        if float(request_json.get('latitude')) < LATITUDE_MIN or float(
                request_json.get('latitude')) > LATITUDE_MAX or float(
            request_json.get('longitude')) < LONGITUDE_MIN or float(request_json.get('longitude')) > LONGITUDE_MAX:
            resp['error'] = 'Latitude and longitude does not correspond to Lyon.'
            return render_template('response.json', response=json.dumps(resp))
        if not request_json.get('keywords'):
            resp['error'] = 'No keywords given.'
            return render_template('response.json', response=json.dumps(resp))

        db = get_db()
        db.execute(
            'INSERT INTO places (lat, long, address, phone, website, openning_hours, name, description, id_user, note_5, nb_vote) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)',
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
        cur = db.execute('SELECT * FROM places WHERE lat=? AND long=?',
                         [float(request_json.get('latitude')), float(request_json.get('longitude'))])
        place_inserted = cur.fetchone()
        for k in request_json.get('keywords'):
            k = k.upper()
            cur = db.execute('SELECT * FROM keywords WHERE name=?', [k])
            keyword = cur.fetchone()
            if not keyword:
                db.execute('INSERT INTO keywords (name) VALUES (?)', [k])
                db.commit()
                cur = db.execute('SELECT * FROM keywords WHERE name=?', [k])
                keyword = cur.fetchone()
            # on peut inserer la relation place/keyword
            db.execute('INSERT INTO place_keywords (id_place, id_keyword) VALUES (?, ?)',
                       [place_inserted['id'], keyword['id']])
            db.commit()
        resp['status'] = 'OK'

    except:
        resp['error'] = 'An error occured while inserting place.'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/delete-place', methods=['POST'])
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
        resp['error'] = 'Place not found sorry.'
        return render_template('response.json', response=json.dumps(resp))
    if place['id_user'] != user['id']:
        resp['error'] = 'You are not allowed to access or modify this ressource.'
        return render_template('response.json', response=json.dumps(resp))

    db = get_db()
    db.execute('DELETE FROM places WHERE id=?', [place['id']])
    db.execute('DELETE FROM place_keywords WHERE id_place=?', [place['id']])
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
        places = cur.fetchall()
        for index, place in enumerate(places):
            cur = db.execute(
                'SELECT keywords.name FROM keywords,place_keywords WHERE keywords.id=place_keywords.id_keyword AND id_place=?',
                [place['id']])
            places[index]['keywords'] = cur.fetchall()
        resp['status'] = 'OK'
        resp['places'] = places
    except:
        resp['error'] = 'An error occured while getting places.'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/get-place-coord/<float:lat>,<float:longitude>', methods=['GET'])
def get_place_coord(lat, longitude):
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    try:
        db = get_db()
        cur = db.execute('SELECT * FROM places WHERE lat=? AND long=?', [lat, longitude])
        place = cur.fetchone()
        cur = db.execute(
            'SELECT keywords.name FROM keywords,place_keywords WHERE keywords.id=place_keywords.id_keyword AND id_place=?',
            [place['id']])
        place['keywords'] = cur.fetchall()
        resp['status'] = 'OK'
        resp['place'] = place
    except:
        resp['error'] = 'An error occured while getting place.'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/get-place-radius-coord/<float:lat>,<float:longitude>,<int:radius>', methods=['GET'])
def get_place_radius_coord(lat, longitude, radius):
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    try:
        db = get_db()
        cur = db.execute('SELECT * FROM places WHERE (lat>? AND lat<? AND long>? AND long<?)',
                         [lat - (radius * 0.009043), lat + (radius * 0.009043), longitude - (radius * 0.0131043),
                          longitude + (radius * 0.0131043)])

        places = cur.fetchall()

        for index, place in enumerate(places):
            cur = db.execute(
                'SELECT keywords.name FROM keywords,place_keywords WHERE keywords.id=place_keywords.id_keyword AND id_place=?',
                [place['id']])
            places[index]['keywords'] = cur.fetchall()
        resp['status'] = 'OK'
        resp['places'] = places
    except:
        resp['error'] = 'An error occured while getting place.'
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
        if not place:
            resp['error'] = 'Place not found.'
            return render_template('response.json', response=json.dumps(resp))
        resp['status'] = 'OK'
        resp['place'] = place
    except:
        resp['error'] = 'An error occured while getting place.'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/get-places-keyword/', methods=['GET'])
def get_places_keyword():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    keywords = request.args.getlist('keywords')
    for i, keyword in enumerate(keywords):
        keywords[i] = keyword.upper()
    try:
        places_final = []
        first = True
        db = get_db()
        for k in keywords:
            list_places = db.execute(
                'SELECT * FROM places WHERE id IN (SELECT id_place FROM place_keywords WHERE id_keyword IN (SELECT id FROM keywords WHERE name=?))',
                [k])
            places = list_places.fetchall()
            if first:
                places_final = places
            else:
                places_final = list(set(places).intersection(places_final))
        for index, place in enumerate(places_final):
            cur = db.execute(
                'SELECT keywords.name FROM keywords,place_keywords WHERE keywords.id=place_keywords.id_keyword AND id_place=?',
                [place['id']])
            places_final[index]['keywords'] = cur.fetchall()
        resp['status'] = 'OK'
        resp['places'] = places_final
    except:
        resp['error'] = 'An error occured while getting places.'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/update-place', methods=['POST'])
def update_place():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    request_json = request.get_json()
    place_id = request_json.get('id', '-1')
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
        if float(request_json.get('latitude')) < LATITUDE_MIN or float(
                request_json.get('latitude')) > LATITUDE_MAX or float(
            request_json.get('longitude')) < LONGITUDE_MIN or float(request_json.get('longitude')) > LONGITUDE_MAX:
            resp['error'] = 'Latitude and longitude does not correspond to Lyon.'
            return render_template('response.json', response=json.dumps(resp))
        if not request_json.get('keywords'):
            resp['error'] = 'No keywords given.'
            return render_template('response.json', response=json.dumps(resp))

        db = get_db()
        db.execute(
            'UPDATE places SET lat=?, long=?, address=?, phone=?, website=?, openning_hours=?, name=?, description=? WHERE id=?',
            [float(request_json.get('latitude')),
             float(request_json.get('longitude')),
             request_json.get('address'),
             request_json.get('phone'),
             request_json.get('website'),
             request_json.get('openning_hours'),
             request_json.get('name'),
             request_json.get('description'),
             place['id']])
        db.commit()
        place = get_place(place_id)
        db.execute('DELETE FROM place_keywords WHERE id_place=?', [place['id']])
        db.commit()
        for k in request_json.get('keywords'):
            k = k.upper()
            cur = db.execute('SELECT * FROM keywords WHERE name=?', [k])
            keyword = cur.fetchone()
            if not keyword:
                db = get_db()
                db.execute('INSERT INTO keywords (name) VALUES (?)', [k])
                db.commit()
                cur = db.execute('SELECT * FROM keywords WHERE name=?', [k])
                keyword = cur.fetchone()
            # on peut inserer la relation place/keyword
            db.execute('INSERT INTO place_keywords (id_place, id_keyword) VALUES (?, ?)',
                       [place['id'], keyword['id']])
            db.commit()

        resp['status'] = 'OK'
    except:
        resp['error'] = 'An error occured while updating place.'

    return render_template('response.json', response=json.dumps(resp))


@app.route('/get-all-places-keywords', methods=['GET'])
def get_all_places_keywords():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    try:
        db = get_db()
        keywords = db.execute('SELECT * FROM keywords WHERE id IN (SELECT id_keyword FROM place_keywords)', [])
        resp['status'] = 'OK'
        resp['keywords'] = keywords.fetchall()
    except:
        resp['error'] = 'An error occured while getting places keywords.'
    return render_template('response.json', response=json.dumps(resp))


def recalculate_vote_place(place):
    db = get_db()
    cur = db.execute("SELECT AVG(vote) AS vote_moyen FROM vote_user_place WHERE id_place=?", [place['id']])
    note_moy = cur.fetchone()
    db.execute("UPDATE places SET nb_vote=?, note_5=? WHERE id=?", [place['nb_vote']+1, note_moy['vote_moyen'], place['id']])
    db.commit()


@app.route('/vote-place', methods=['POST'])
def vote_place():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))
    request_json = request.get_json()
    place_id = request_json.get('id')
    place = get_place(place_id)
    note = float(request_json.get('note'))
    if place is None:
        resp['error'] = "Place not found."
        return render_template('response.json', response=json.dumps(resp))
    if note < 0 or note > 5:
        resp['error'] = "Note should be between 0 and 5."
        return render_template('response.json', response=json.dumps(resp))
    try:
        db = get_db()
        cur = db.execute("SELECT * FROM vote_user_place WHERE id_user=? AND id_place=?", [session['user_id'], place_id])
        vote = cur.fetchone()
        if vote is None:
            db.execute("INSERT INTO vote_user_place (id_user, id_place, vote) VALUES (?, ?, ?)", [session['user_id'], place_id, note])
        else:
            db.execute("UPDATE vote_user_place SET vote=? WHERE id_user=? AND id_place=?", [note, session['user_id'], place_id])
        db.commit()
        cur = db.execute("SELECT * FROM places WHERE id=?", [place_id])
        place = cur.fetchone()
        recalculate_vote_place(place)
        resp['status'] = 'OK'
    except ValueError:
        resp['error'] = 'An error occured while voting.'
    return render_template('response.json', response=json.dumps(resp))


##########################################################################################
#                                     END PLACES
##########################################################################################
#                                       USERS
##########################################################################################


@app.route('/login', methods=['POST'])
def login():
    import hashlib
    request_json = request.get_json()
    password = hashlib.sha256(request_json.get('password', 'bla').encode('utf-8')).hexdigest()
    db = get_db()
    cur = db.execute('SELECT * FROM users WHERE password=? AND username=?',
                     [password, request_json.get('username', 'bla')])
    user = cur.fetchone()
    resp = {
        'status': 'KO'
    }
    if user is not None:
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
        cur = db.execute('SELECT * FROM users WHERE username=?', [username])
        user = cur.fetchone()
        if user is None:
            db.execute('INSERT INTO USERS (email, password, username) VALUES (?, ?, ?)',
                       [email, password, username])
            db.commit()
            cur = db.execute('SELECT * FROM users WHERE password=? AND username=?',
                             [password, request_json.get('username', 'bla')])
            user = cur.fetchone()
            if user is not None:
                session['user_id'] = user['id']
                resp['status'] = 'OK'
                resp['username'] = user['username']
                resp['email'] = user['email']
        else:
            resp['error'] = 'Sorry, username already exists.'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/delete-user', methods=['POST'])
def delete_user():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    user = get_user(session['user_id'])
    if not user:
        resp['error'] = 'User not found sorry.'
        return render_template('response.json', response=json.dumps(resp))
    db = get_db()
    db.execute('DELETE FROM users WHERE id=?', [user['id']])
    db.commit()
    session.pop('user_id', None)
    resp['status'] = 'OK'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    resp = {
        'status': 'OK'
    }
    return render_template('response.json', response=json.dumps(resp))


##########################################################################################
#                                     END USER
##########################################################################################
#                                     CIRCUITS
##########################################################################################


def request_api_google(places):
    if USE_API:
        virgule = '%2C'
        pipe = '%7C'

        place_origin = get_place(places[0])
        place_dest = get_place(places[-1])
        if place_origin is None or place_dest is None:
            return None, None
        origin = str(place_origin['lat']) + virgule + str(place_origin['long'])
        destination = str(place_dest['lat']) + virgule + str(place_dest['long'])

        places = places[1:-1]
        waypoints = ''
        for p_id in places:
            place = get_place(p_id)
            if place is None:
                return None, None
            waypoints += str(place['lat']) + virgule + str(place['long']) + pipe
        waypoints = waypoints[0:-3]
        try:
            import requests
            url_api_directions = 'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&waypoints={waypoints}&key=AIzaSyCwFv6LLGksQxm-YFoVrrmbx9ip3xPbdDA&mode=walking'
            url_api_elevation = 'https://maps.googleapis.com/maps/api/elevation/json?path={path}&samples={samples}&key=AIzaSyCwFv6LLGksQxm-YFoVrrmbx9ip3xPbdDA&mode=walking'

            resp_direction = requests.get(url_api_directions.format(origin=origin, destination=destination, waypoints=waypoints))
            result = json.loads(resp_direction.text)
            legs = result['routes'][0]['legs']
            path = str(legs[0]['steps'][0]['start_location']['lat']) + virgule + str(legs[0]['steps'][0]['start_location']['lng']) + pipe

            calc_length = 0
            number_locations = 0
            for leg in legs:
                calc_length += leg['distance']['value']
                for step in leg['steps']:
                    path += str(step['end_location']['lat']) + virgule + str(step['end_location']['lng']) + pipe
                    number_locations += 1
            path = path[0:-3]
            resp_elevation = requests.get(url_api_elevation.format(path=path, samples=str(number_locations)))
            result_elevation = json.loads(resp_elevation.text)

            old_elevation_m = -1
            calc_height = 0
            for loc in result_elevation["results"]:
                if old_elevation_m != -1:
                    diff = old_elevation_m - loc["elevation"]
                    if diff > 0:
                        calc_height += diff
                old_elevation_m = loc["elevation"]
            return calc_length / 1000, calc_height
        except:
            return None, None
    else:
        return 3, 20


@app.route('/add-circuit', methods=['POST'])
def add_circuit():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    request_json = request.get_json()
    try:
        if not request_json.get('keywords'):
            resp['error'] = 'No keywords given.'
            return render_template('response.json', response=json.dumps(resp))
        if not request_json.get('places'):
            resp['error'] = 'No places given.'
            return render_template('response.json', response=json.dumps(resp))

        calc_length, calc_height = request_api_google(request_json.get('places'))
        if calc_length is None or calc_height is None:
            resp['error'] = 'Wrong path : a place does not exists.'
            return render_template('response.json', response=json.dumps(resp))

        db = get_db()
        db.execute(
            'INSERT INTO circuit (name, description, length_km, height_difference_m, note_5, nb_vote, id_user) VALUES (?, ?, ?, ?, 0, 0, ?)',
            [request_json.get('name'),
             request_json.get('description'),
             calc_length,
             calc_height,
             session.get('user_id')])
        db.commit()
        cur = db.execute('SELECT * FROM circuit WHERE id=last_insert_rowid()')
        circuit_inserted = cur.fetchone()
        for k in request_json.get('keywords'):
            k = k.upper()
            cur = db.execute('SELECT * FROM keywords WHERE name=?', [k])
            keyword = cur.fetchone()
            if not keyword:
                db.execute('INSERT INTO keywords (name) VALUES (?)', [k])
                db.commit()
                cur = db.execute('SELECT * FROM keywords WHERE name=?', [k])
                keyword = cur.fetchone()
            # on peut inserer la relation place/keyword
            db.execute('INSERT INTO circuit_keywords (id_circuit, id_keyword) VALUES (?, ?)',
                       [circuit_inserted['id'], keyword['id']])
            db.commit()
        for index, p in enumerate(request_json.get('places')):
            cur = db.execute('SELECT * FROM places WHERE id=?', [p])
            place = cur.fetchone()
            if place:
                db.execute('INSERT INTO circuit_places (id_circuit, id_place, number_in_list) VALUES (?,?,?)',
                           [circuit_inserted['id'], p, index])
                db.commit()
        resp['status'] = 'OK'
    except:
        resp['error'] = 'An error occured while inserting circuit.'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/update-circuit', methods=['POST'])
def update_circuit():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    request_json = request.get_json()
    circuit_id = request_json.get('id', '-1')
    user = get_user(session['user_id'])
    circuit = get_circuit(circuit_id)
    if not user:
        resp['error'] = 'User not found sorry.'
        return render_template('response.json', response=json.dumps(resp))
    if not circuit:
        resp['error'] = 'Circuit not found sorry.'
        return render_template('response.json', response=json.dumps(resp))
    if circuit['id_user'] != user['id']:
        resp['error'] = 'You are not allowed to access or modify this ressource.'
        return render_template('response.json', response=json.dumps(resp))

    try:
        if not request_json.get('keywords'):
            resp['error'] = 'No keywords given.'
            return render_template('response.json', response=json.dumps(resp))
        if not request_json.get('places'):
            resp['error'] = 'No places given.'
            return render_template('response.json', response=json.dumps(resp))

        calc_length, calc_height = request_api_google(request_json.get('places'))
        if calc_length is None or calc_height is None:
            resp['error'] = 'Wrong path : a place does not exists.'
            return render_template('response.json', response=json.dumps(resp))

        db = get_db()
        db.execute(
            'UPDATE circuit SET name=?, description=?, length_km=?, height_difference_m=? WHERE id=?',
            [request_json.get('name'),
             request_json.get('description'),
             calc_length,
             calc_height,
             circuit_id])
        db.commit()
        circuit = get_circuit(circuit_id)
        db.execute('DELETE FROM circuit_keywords WHERE id_circuit=?', [circuit['id']])
        db.execute('DELETE FROM circuit_places WHERE id_circuit=?', [circuit['id']])
        db.commit()
        for k in request_json.get('keywords'):
            k = k.upper()
            cur = db.execute('SELECT * FROM keywords WHERE name=?', [k])
            keyword = cur.fetchone()
            if not keyword:
                db = get_db()
                db.execute('INSERT INTO keywords (name) VALUES (?)', [k])
                db.commit()
                cur = db.execute('SELECT * FROM keywords WHERE name=?', [k])
                keyword = cur.fetchone()
            # on peut inserer la relation place/keyword
            db.execute('INSERT INTO circuit_keywords (id_circuit, id_keyword) VALUES (?, ?)',
                       [circuit['id'], keyword['id']])
            db.commit()
        for index, p in enumerate(request_json.get('places')):
            cur = db.execute('SELECT * FROM places WHERE id=?', [p])
            place = cur.fetchone()
            if place:
                db.execute('INSERT INTO circuit_places (id_circuit, id_place, number_in_list) VALUES (?,?,?)',
                           [circuit['id'], p, index])
                db.commit()

        resp['status'] = 'OK'
    except:
        resp['error'] = 'An error occured while updating place.'

    return render_template('response.json', response=json.dumps(resp))


@app.route('/get-circuit-id/<int:circuit_id>', methods=['GET'])
def get_circuit_id(circuit_id):
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))
    try:
        circuit = get_circuit(circuit_id)
        if not circuit:
            resp['error'] = 'Circuit not found.'
            return render_template('response.json', response=json.dumps(resp))
        resp['status'] = 'OK'
        resp['circuit'] = circuit
    except:
        resp['error'] = 'An error occured while getting place.'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/get-circuits-keyword/', methods=['GET'])
def get_circuits_keyword():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    keywords = request.args.getlist('keywords')
    for i, keyword in enumerate(keywords):
        keywords[i] = keyword.upper()
    try:
        circuits_final = []
        first = True
        db = get_db()
        for k in keywords:
            list_circuits = db.execute(
                'SELECT * FROM circuit WHERE id IN (SELECT id_circuit FROM circuit_keywords WHERE id_keyword IN (SELECT id FROM keywords WHERE name=?))',
                [k])
            circuits = list_circuits.fetchall()
            if first:
                circuits_final = circuits
            else:
                circuits_final = list(set(circuits).intersection(circuits_final))
        for index, circuit in enumerate(circuits_final):
            cur = db.execute(
                'SELECT keywords.name FROM keywords,circuit_keywords WHERE keywords.id=circuit_keywords.id_keyword AND id_circuit=?',
                [circuit['id']])
            circuits_final[index]['keywords'] = cur.fetchall()
        resp['status'] = 'OK'
        resp['circuits'] = circuits_final
    except:
        resp['error'] = 'An error occured while getting circuits.'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/get-all-circuits-keywords', methods=['GET'])
def get_all_circuits_keywords():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    try:
        db = get_db()
        circuits = db.execute('SELECT * FROM keywords WHERE id IN (SELECT id_circuit FROM circuit_keywords)', [])
        resp['status'] = 'OK'
        resp['keywords'] = circuits.fetchall()
    except:
        resp['error'] = 'An error occured while getting circuits keywords.'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/delete-circuit', methods=['POST'])
def delete_circuit():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    request_json = request.get_json()
    user = get_user(session['user_id'])
    circuit = get_circuit(request_json.get('circuit_id', '-1'))
    if not user:
        resp['error'] = 'User not found sorry.'
        return render_template('response.json', response=json.dumps(resp))
    if not circuit:
        resp['error'] = 'Circuit not found sorry.'
        return render_template('response.json', response=json.dumps(resp))
    if circuit['id_user'] != user['id']:
        resp['error'] = 'You are not allowed to access or modify this ressource.'
        return render_template('response.json', response=json.dumps(resp))

    db = get_db()
    db.execute('DELETE FROM circuit WHERE id=?', [circuit['id']])
    db.execute('DELETE FROM circuit_keywords WHERE id_circuit=?', [circuit['id']])
    db.commit()
    resp['status'] = 'OK'
    return render_template('response.json', response=json.dumps(resp))


@app.route('/get-circuits', methods=['GET'])
def get_circuits():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))

    try:
        db = get_db()
        cur = db.execute('SELECT * FROM circuit')
        list_circuits = cur.fetchall()
        for index, circuit in enumerate(list_circuits):
            cur = db.execute(
                'SELECT keywords.name FROM keywords,circuit_keywords WHERE keywords.id=circuit_keywords.id_keyword AND id_circuit=?',
                [circuit['id']])
            list_circuits[index]['keywords'] = cur.fetchall()
        resp['status'] = 'OK'
        resp['circuits'] = list_circuits
    except:
        resp['error'] = 'An error occured while getting circuits.'
    return render_template('response.json', response=json.dumps(resp))


def recalculate_vote_circuit(circuit):
    db = get_db()
    cur = db.execute("SELECT AVG(vote) AS vote_moyen FROM vote_user_circuit WHERE id_circuit=?", [circuit['id']])
    note_moy = cur.fetchone()
    db.execute("UPDATE circuit SET nb_vote=?, note_5=? WHERE id=?", [circuit['nb_vote']+1, note_moy['vote_moyen'], circuit['id']])
    db.commit()


@app.route('/vote-circuit', methods=['POST'])
def vote_circuit():
    resp = {
        'status': 'KO'
    }
    if not session.get('user_id'):
        resp['error'] = 'Please login or register to access our services.'
        return render_template('response.json', response=json.dumps(resp))
    request_json = request.get_json()
    circuit_id = request_json.get('id')
    circuit = get_circuit(circuit_id)
    note = float(request_json.get('note'))
    if circuit is None:
        resp['error'] = "Circuit not found."
        return render_template('response.json', response=json.dumps(resp))
    if note < 0 or note > 5:
        resp['error'] = "Note should be between 0 and 5."
        return render_template('response.json', response=json.dumps(resp))
    try:
        db = get_db()
        cur = db.execute("SELECT * FROM vote_user_circuit WHERE id_user=? AND id_circuit=?", [session['user_id'], circuit_id])
        vote = cur.fetchone()
        if vote is None:
            db.execute("INSERT INTO vote_user_circuit (id_user, id_circuit, vote) VALUES (?, ?, ?)", [session['user_id'], circuit_id, note])
        else:
            db.execute("UPDATE vote_user_circuit SET vote=? WHERE id_user=? AND id_circuit=?", [note, session['user_id'], circuit_id])
        db.commit()
        cur = db.execute("SELECT * FROM circuit WHERE id=?", [circuit_id])
        circuit = cur.fetchone()
        recalculate_vote_circuit(circuit)
        resp['status'] = 'OK'
    except:
        resp['error'] = 'An error occured while voting.'
    return render_template('response.json', response=json.dumps(resp))


##########################################################################################
#                                     END CIRCUITS
##########################################################################################

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
