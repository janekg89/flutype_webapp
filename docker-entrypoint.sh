#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py makemigrations flutype
python manage.py makemigrations
python manage.py migrate

# Fill database with test dataset
python ./flutype/data_management/fill_users.py
python ./flutype/data_management/fill_database.py

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000