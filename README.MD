# django web + API
django version 3.1
Mysql
hosted on 87

# Create database
1. CREATE USER 'leave_management'@'localhost' IDENTIFIED BY '8uQ#]CaM#SvLbeKa';
2. GRANT ALL PRIVILEGES ON leave_management.* to 'root'@'localhost';
3. CREATE DATABASE leave_management CHARACTER SET utf8 COLLATE utf8_unicode_ci;
4. DROP DATABASE leave_management;

# create virtual venv
virtualenv --python=/usr/bin/python3.6 venv