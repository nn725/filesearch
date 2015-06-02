drop table if exists accounts;
create table accounts (
	id integer primary key autoincrement,
	service text not null,
	key integer not null
);