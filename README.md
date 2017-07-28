# flutype_webapp

## Installation
```
mkvirtualenv flutype_webapp
pip install -r requirements.txt
```

## Start the App
```
cd flutype_webapp
./docker-entrypoint.sh
```

## pycharm integration
right click `db.sqlite3` -> As Data Source



## Docker container
Install docker via `docker-ce` on the system.

Run the app via
```
docker-compose up
```

# gunicorn & deployment
gunicorn --bind 0.0.0.0:8000 flutype_webapp.wsgi:application

