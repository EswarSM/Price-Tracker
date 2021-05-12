create database Pricetracker2;

use pricetracker2;

create table User
(
emailID int auto_increment primary key,
name varchar(50) not null,
email varchar(100) unique not null,
phonenumber varchar(15) not null
);

insert into user (name, email, phonenumber) values('1','2','3');

