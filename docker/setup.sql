-- create the databases
CREATE DATABASE IF NOT EXISTS flaskdb;

-- create the users for each database
CREATE USER 'flaskuser'@'%' IDENTIFIED BY '1234';
GRANT CREATE, ALTER, INDEX, LOCK TABLES, REFERENCES, UPDATE, DELETE, DROP, SELECT, INSERT ON `flaskdb`.* TO 'flaskuser'@'%';

FLUSH PRIVILEGES;