# flutype_webapp

## Installation
```
mkvirtualenv flutype_webapp
pip install -r requirements.txt
```

## Start the App
```
cd flutype_webapp
python manage.py runserver
```

## pycharm integration
right click `db.sqlite3` -> As Data Source


# gunicorn & deployment
gunicorn --bind 0.0.0.0:8000 myproject.wsgi