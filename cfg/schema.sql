

CREATE DATABASE IF NOT EXISTS smarthome ;
# CREATE USER 'smarthome'@'localhost' IDENTIFIED BY 'password1';
GRANT SELECT, INSERT, UPDATE, DELETE ON smarthome.* to 'smarthone'@'%';

USE smarthome;
CREATE TABLE IF NOT EXISTS temp_raw (
    time DATETIME,
    temp DECIMAL(3,2),
    light INT
);

CREATE TABLE IF NOT EXISTS temp_hourly (
    time DATETIME,
    temp DECIMAL(3,2),
    light INT
);


