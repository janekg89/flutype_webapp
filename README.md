<img alt="flutype logo" src="./docs/logo/flutype-logo-v3.png" height="75"/>

# flutype webapp
## Introduction
This project develops a web application for the data management of binding assays for the classification of influenza subtypes.
 
The production version is available at
[http://www.flutype.de](http://www.flutype.de).

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
Install docker via `docker-ce` and `docker-compose` on the system.

Run the app via
```
docker-compose up
```

# gunicorn & deployment
gunicorn --bind 0.0.0.0:8000 flutype_webapp.wsgi:application

# install PhantomJS
 follow: https://www.vultr.com/docs/how-to-install-phantomjs-on-ubuntu-16-04
&copy; 2017 flutype