#!/usr/bin/env bash
########################################################
# Setup the database
#
# Deletes old database and recreates all data.
########################################################
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# delete old database files & uploads

# for postgres
#sudo su postgres
#psql
#drop database flutype;
#create database flutype with owner flutype_user;
#\q
#exit

cd $DIR
rm ./media/db.sqlite3
rm -rf flutype/migrations/*

# clean setup
python manage.py makemigrations
python manage.py makemigrations flutype
python manage.py migrate

# clean everything
echo "* Remove cache *"
rm -rf media/CACHE/*

echo "* Upload archives *"
# python manage.py flush
python flutype/data_management/fill_users.py
python flutype/data_management/fill_database.py
