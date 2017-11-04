set foreign_key_checks = 0;
drop table if exists customerorder;
drop table if exists dealerorder;
drop table if exists corderline;
drop table if exists dorderline;
drop table if exists items;
drop table if exists customer;
set foreign_key_checks = 1;


create table if not exists items (
	item_id int  not null auto_increment primary key,
	name varchar(50),
	category varchar(50),
	price int,
	brand varchar(50),
	description varchar(1000),
	quantity int default 0
);

create table if not exists customer (
	customer_id int  not null auto_increment primary key,
	name varchar(50),
	email varchar(50),
	phone varchar(50),
	address varchar(200),
	user int,
	points int default 0,
	purchases int default 0,
	foreign key(user) references auth_user(id)
);

create table if not exists dealer (
	dealer_id int  not null auto_increment primary key,
	name varchar(50),
	email varchar(50),
	phone varchar(50),
	address varchar(200)
);

create table if not exists customerorder (
	order_id int  not null auto_increment primary key,
	customer_id int,
	date datetime default now(),
	status varchar(20) default "Pending",
	total int,
	placed int default 0,
	foreign key(customer_id) references customer(customer_id) on delete cascade
);

create table if not exists corderline (
	order_id int,
	item_id int,
	quantity int,
	foreign key(order_id) references customerorder(order_id) on delete cascade,
	foreign key(item_id) references items(item_id) on delete cascade	
);

create table if not exists dealerorder (
	order_id int  not null auto_increment primary key,
	dealer_id int,
	date datetime default now(),
	total int,
	status varchar(20) default "Pending",
	dateexpected date,
	foreign key(dealer_id) references dealer(dealer_id) on delete cascade
);

create table if not exists dorderline (
	order_id int,
	item_id int,
	quantity int,
	foreign key(order_id) references dealerorder(order_id) on delete cascade,
	foreign key(item_id) references items(item_id) on delete cascade	
);