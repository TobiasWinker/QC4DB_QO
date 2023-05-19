create table "circuits" (
  "circuitid" int not null,
  "circuitref" varchar(255) not null default '',
  "name" varchar(255) not null default '',
  "location" varchar(255) default null,
  "country" varchar(255) default null,
  "lat" float default null,
  "lng" float default null,
  "alt" int default null,
  "url" varchar(255) not null default '',
  primary key ("circuitid")
);

create table "constructorresults" (
  "constructorresultsid" int not null,
  "raceid" int not null default '0',
  "constructorid" int not null default '0',
  "points" float default null,
  "status" varchar(255) default null,
  primary key ("constructorresultsid")
);

create table "constructorstandings" (
  "constructorstandingsid" int not null,
  "raceid" int not null default '0',
  "constructorid" int not null default '0',
  "points" float not null default '0',
  "position" int default null,
  "positiontext" varchar(255) default null,
  "wins" int not null default '0',
  primary key ("constructorstandingsid")
);

create table "constructors" (
  "constructorid" int not null,
  "constructorref" varchar(255) not null default '',
  "name" varchar(255) not null default '',
  "nationality" varchar(255) default null,
  "url" varchar(255) not null default '',
  primary key ("constructorid")
);

create table "driverstandings" (
  "driverstandingsid" int not null,
  "raceid" int not null default '0',
  "driverid" int not null default '0',
  "points" float not null default '0',
  "position" int default null,
  "positiontext" varchar(255) default null,
  "wins" int not null default '0',
  primary key ("driverstandingsid")
);

create table "drivers" (
  "driverid" int not null,
  "driverref" varchar(255) not null default '',
  "number" int default null,
  "code" varchar(3) default null,
  "forename" varchar(255) not null default '',
  "surname" varchar(255) not null default '',
  "dob" date default null,
  "nationality" varchar(255) default null,
  "url" varchar(255) not null default '',
  primary key ("driverid")  
);

create table "laptimes" (
  "raceid" int not null,
  "driverid" int not null,
  "lap" int not null,
  "position" int default null,
  "time" varchar(255) default null,
  "milliseconds" int default null,
  primary key ("raceid","driverid","lap")
);

create table "pitstops" (
  "raceid" int not null,
  "driverid" int not null,
  "stop" int not null,
  "lap" int not null,
  "time" time not null,
  "duration" varchar(255) default null,
  "milliseconds" int default null,
  primary key ("raceid","driverid","stop")
);

create table "qualifying" (
  "qualifyid" int not null,
  "raceid" int not null default '0',
  "driverid" int not null default '0',
  "constructorid" int not null default '0',
  "number" int not null default '0',
  "position" int default null,
  "q1" varchar(255) default null,
  "q2" varchar(255) default null,
  "q3" varchar(255) default null,
  primary key ("qualifyid")
);

create table "races" (
  "raceid" int not null,
  "year" int not null default '0',
  "round" int not null default '0',
  "circuitid" int not null default '0',
  "name" varchar(255) not null default '',
  "date" date not null default '2000-01-01',
  "time" time default null,
  "url" varchar(255) default null,
  "fp1_date" date default null,
  "fp1_time" time default null,
  "fp2_date" date default null,
  "fp2_time" time default null,
  "fp3_date" date default null,
  "fp3_time" time default null,
  "quali_date" date default null,
  "quali_time" time default null,
  "sprint_date" date default null,
  "sprint_time" time default null,
  primary key ("raceid")  
);

create table "results" (
  "resultid" int not null,
  "raceid" int not null default '0',
  "driverid" int not null default '0',
  "constructorid" int not null default '0',
  "number" int default null,
  "grid" int not null default '0',
  "position" int default null,
  "positiontext" varchar(255) not null default '',
  "positionorder" int not null default '0',
  "points" float not null default '0',
  "laps" int not null default '0',
  "time" varchar(255) default null,
  "milliseconds" int default null,
  "fastestlap" int default null,
  "rank" int default '0',
  "fastestlaptime" varchar(255) default null,
  "fastestlapspeed" varchar(255) default null,
  "statusid" int not null default '0',
  primary key ("resultid")
);

create table "seasons" (
  "year" int not null default '0',
  "url" varchar(255) not null default '',
  primary key ("year")
);

create table "sprintresults" (
  "sprintresultid" int not null,
  "raceid" int not null default '0',
  "driverid" int not null default '0',
  "constructorid" int not null default '0',
  "number" int not null default '0',
  "grid" int not null default '0',
  "position" int default null,
  "positiontext" varchar(255) not null default '',
  "positionorder" int not null default '0',
  "points" float not null default '0',
  "laps" int not null default '0',
  "time" varchar(255) default null,
  "milliseconds" int default null,
  "fastestlap" int default null,
  "fastestlaptime" varchar(255) default null,
  "statusid" int not null default '0',
  primary key ("sprintresultid")
);

create table "status" (
  "statusid" int not null,
  "status" varchar(255) not null default '',
  primary key ("statusid")
);
