Go into `C:\Program Files\MySQL\MySQL Server 8.0\bin`

Create a DB user account used to connect to mysql from vscode

mysql -u root -p
Add new user account
mysql> CREATE USER 'sqluser'@'%' IDENTIFIED 
 -> WITH mysql_native_password BY 'password' ; 
Provide with all privileges
mysql> GRANT ALL PRIVILEGES ON *.* TO 'sqluser'@'%' ;
Validate privileges
mysql> FLUSH PRIVILEGES;

Vscode connects to mysql

host: localhost
user: sqluser
password: password
port: 3306
cert: 'Enter'

Run predefine.sql