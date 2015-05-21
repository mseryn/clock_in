PRAGMA foreign_keys = OFF;

drop table if exists users;

create table users (id integer primary key autoincrement, username text unique not null, password text not null, admin boolean);
insert into users (username, password, admin) VALUES ('mdooley1', '46d2f4d5ccd31e60dbef4e98f60170fa', 1);

drop table if exists history;

create table history (id integer primary key, userid INTEGER not null, checkin datetime not null, checkout datetime, FOREIGN KEY(userid) REFERENCES users(id)); 
