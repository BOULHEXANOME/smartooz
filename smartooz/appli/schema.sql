DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id integer primary key autoincrement,
  email text not null,
  password text not null,
  username text unique not null
);

DROP TABLE IF EXISTS keywords;
CREATE TABLE keywords (
  id integer primary key autoincrement,
  name text not null
);

DROP TABLE IF EXISTS place_keywords;
CREATE TABLE place_keywords (
  id_place_or_circuit integer not null,
  id_keyword integer not null,
  UNIQUE(id_place_or_circuit, id_keyword)
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
  UNIQUE(lat, long)
);

DROP TABLE IF EXISTS circuit_places;
CREATE TABLE circuit_places (
  id_circuit integer not null,
  id_place integer not null,
  UNIQUE(id_place, id_circuit)
);

DROP TABLE IF EXISTS circuit;
CREATE TABLE circuit (
  id integer primary key autoincrement,
  name text not null,
  description text not null,
  length_km float not null,
  height_difference_m float not null,
  note_5 float not null,
  id_user integer not null
);

DELETE FROM users;
DELETE FROM places;
DELETE FROM place_keywords;
DELETE FROM keywords;
DELETE FROM circuit;
DELETE FROM circuit_places;

insert into users (email, password, username) values ('hugoss1@hotmail.fr', 'hugo', 'hugo');
insert into users (email, password, username) values ('hugo@hotmail.fr', 'hugo2', 'hugo2');