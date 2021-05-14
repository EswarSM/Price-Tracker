use pricetracker2;

create table tracker
(
time varchar(100) primary key,
productID int,
price varchar(100)
);

insert into tracker values('Essakrim','6','10')