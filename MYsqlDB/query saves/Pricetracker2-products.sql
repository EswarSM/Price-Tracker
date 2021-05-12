use pricetracker2;

create table products(
productID int auto_increment primary key,
title varchar(240) not null,
emailID int not null,
url varchar(240) not null,
duration varchar(10) not null,
price varchar(50) not null
);

select * from products;

alter table products add column notification varchar(2);

update products set notification = '0' where productID = 1;

insert into products (title, emailID, url, duration, price, notification) values ('1','2','3','4','5','6');

delete from products where productId = 5; 