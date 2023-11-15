-- -- create DB
-- create database OnlineForumPlatform;

-- -- create table saving user information
-- create table OnlineForumPlatform.UserInformation
-- (
-- 	email varchar(128) not null,
-- 	nickname nvarchar(100) default 'NULL' null,
-- 	password varchar(128) not null,
-- 	type int default '0' null,
-- 	create_time datetime default '1999-9-9 9:9:9' not null,
-- 	phone varchar(128) null,
-- 	constraint UserInformation_pk
-- 		primary key (email)
-- );

-- -- Drop user account
-- drop user 'sitongliu9'

-- -- create table saving issues
-- create table OnlineForumPlatform.Issue
-- (
-- 	Ino varchar(128) null,
-- 	email varchar(128) not null,
-- 	title text default null,
-- 	issue_time datetime null,
-- 	constraint Issue_UserInformation_email_fk
-- 		foreign key (email) references UserInformation (email)
-- );

-- create unique index Issue_Ino_uindex
-- 	on OnlineForumPlatform.Issue (Ino);

-- alter table OnlineForumPlatform.Issue
-- 	add constraint Issue_pk
-- 		primary key (Ino);

-- -- create table saving comments
-- create table OnlineForumPlatform.Comment
-- (
-- 	Cno varchar(128) not null,
-- 	Ino varchar(128) not null,
-- 	comment text null,
-- 	comment_time datetime default '1999-9-9 9:9:9' not null,
-- 	email varchar(128) null,
-- 	constraint Comment_pk
-- 		primary key (Cno, Ino),
-- 	constraint Comment_Issue_Ino_fk
-- 		foreign key (Ino) references OnlineForumPlatform.Issue (Ino),
-- 	constraint Comment_UserInformation_email_fk
-- 		foreign key (email) references OnlineForumPlatform.UserInformation (email)
-- );




select * from `onlineforumplatform`.`comment`
