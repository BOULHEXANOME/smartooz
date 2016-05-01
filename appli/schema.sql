DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id integer primary key autoincrement,
  email text unique not null,
  password text not null,
  username text unique not null
);

DROP TABLE IF EXISTS keywords;
CREATE TABLE keywords (
  id integer primary key autoincrement,
  name text unique not null
);

DROP TABLE IF EXISTS place_keywords;
CREATE TABLE place_keywords (
  id_place integer not null,
  id_keyword integer not null,
  UNIQUE(id_place, id_keyword)
);

DROP TABLE IF EXISTS circuit_keywords;
CREATE TABLE circuit_keywords (
  id_circuit integer not null,
  id_keyword integer not null,
  UNIQUE(id_circuit, id_keyword)
);

DROP TABLE IF EXISTS places;
CREATE TABLE places (
  id integer primary key autoincrement,
  lat float not null,
  long float not null,
  address text,
  phone text,
  website text,
  openning_hours text,
  name text not null,
  description text not null,
  id_user integer not null,
  note_5 float not null,
  nb_vote integer not null,
  UNIQUE(lat, long)
);

DROP TABLE IF EXISTS circuit_places;
CREATE TABLE circuit_places (
  id_circuit integer not null,
  id_place integer not null,
  number_in_list integer not null,
  UNIQUE(id_place, id_circuit)
);

DROP TABLE IF EXISTS photo_circuit_place_user;
CREATE TABLE photo_circuit_place_user (
  id_place integer not null,
  id_circuit integer not null,
  id_user integer not null,
  UNIQUE(id_place, id_circuit, id_user)

);

DROP TABLE IF EXISTS circuit;
CREATE TABLE circuit (
  id integer primary key autoincrement,
  name text not null,
  description text not null,
  length_km float not null,
  height_difference_m float not null,
  note_5 float not null,
  nb_vote integer not null,
  id_user integer not null
);

DROP TABLE IF EXISTS vote_user_place;
CREATE TABLE vote_user_place (
  id_user integer not null,
  id_place integer not null,
  vote float not null,
  UNIQUE(id_place, id_user)
);

DROP TABLE IF EXISTS vote_user_circuit;
CREATE TABLE vote_user_circuit (
  id_user integer not null,
  id_circuit integer not null,
  vote float not null,
  UNIQUE(id_circuit, id_user)
);

DROP TABLE IF EXISTS user_did_circuit;
CREATE TABLE user_did_circuit (
  id_user integer not null,
  id_circuit integer not null,
  date_performed datetime not null,
  UNIQUE(id_circuit, id_user, date_performed)
);

DELETE FROM users;
DELETE FROM places;
DELETE FROM place_keywords;
DELETE FROM keywords;
DELETE FROM circuit;
DELETE FROM circuit_places;
DELETE FROM vote_user_place;
DELETE FROM vote_user_circuit;
DELETE FROM user_did_circuit;
