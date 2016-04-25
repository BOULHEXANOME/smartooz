drop table if exists USERS;
create table USERS (
  id integer primary key autoincrement,
  email text not null,
  password text not null,
  username text unique not null,
  is_admin integer not null
);

drop table if exists ARTICLES;
create table ARTICLES (
  id integer primary key autoincrement,
  price integer not null,
  is_accepted integer not null,
  is_read integer not null,
  photo text not null,
  name text not null,
  description text not null,
  id_user integer not null
);

DELETE FROM USERS;
DELETE FROM ARTICLES;

insert into USERS (email, password, username, is_admin) values ('hugoss1@hotmail.fr', 'hihi', 'hugo', 1);
insert into USERS (email, password, username, is_admin) values ('hugo@hotmail.fr', 'bla', 'hugo2', 0);

insert into ARTICLES (name, price, is_accepted, is_read, photo, description, id_user) values ('Cafetiere toute neuve', 50, 0, 0, 'https://images.duckduckgo.com/iu/?u=http%3A%2F%2Fi2.cdscdn.com%2Fpdt2%2F8%2F2%2F6%2F1%2F700x700%2Fbia8006363039826%2Frw%2Fmachine-a-cafe-italienne-bialetti-dama-glamour.jpg&f=1', 'superbe cafetière', 1);
insert into ARTICLES (name, price, is_accepted, is_read, photo, description, id_user) values ('Cafetiere de m***e', 75, 1, 0, 'https://images.duckduckgo.com/iu/?u=http%3A%2F%2Fi2.cdscdn.com%2Fpdt2%2F8%2F2%2F6%2F1%2F700x700%2Fbia8006363039826%2Frw%2Fmachine-a-cafe-italienne-bialetti-dama-glamour.jpg&f=1', "j'essaie de refiler une cafetière que l'on m'a vendu sur ce site de m***" , 2);
