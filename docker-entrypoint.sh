#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py makemigrations
python manage.py makemigrations flutype
python manage.py migrate

# Fill database with test dataset
python ./flutype/data_management/fill_users.py
# python ./flutype/data_management/fill_database.py

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000