--1. CUSTOMERS TABLE
create table customers (
	customer_id SERIAL primary key,
	first_name VARCHAR(50) not null,
	last_name VARCHAR(50) not null,
	email VARCHAR(100) not null unique,
	city VARCHAR(50),
	state VARCHAR(50),
	signup_date DATE not null
	);

--2. PRODUCT TABLE
create table products( 
	product_id serial primary key,
	product_name VARCHAR(100) not null,
	category VARCHAR(50) not null,
	price DECIMAL (10,2) not null check (price > 0),
	cost DECIMAL (10,2) not null check (cost > 0)
);

--3. ORDERS TABLE
create table orders (
order_id serial primary key,
customer_id INT not null references customers(customer_id),
order_date DATE not null,
order_status VARCHAR(20) not null

);

--4. ORDER_ITEMS TABLE
create table order_items(
order_item_id serial primary key,
order_id INT not null references orders (order_id),
product_id INT not null references products(product_id),
quantity INT not null check (quantity > 0),
unit_price DECIMAL(10,2) not null check (unit_price >= 0)
);

--5. RETURNS TABLE
create table returns(
	return_id serial primary key,
	order_item_id INT not null references order_items(order_item_id),
	return_quantity INT not null check (return_quantity > 0),
	return_date DATE not null,
	return_reason VARCHAR(100)
);