<img alt="flutype logo" src="./docs/logo/flutype-logo-v3.png" height="75"/>

# flutype webapp
[![Build Status](https://travis-ci.org/janekg89/flutype_webapp.svg?branch=develop)](https://travis-ci.org/janekg89/flutype_webapp)
## Introduction
This project develops a web application for the data management of binding assays for the classification of influenza subtypes.
 
The production version is available at
[http://www.flutype.de](http://www.flutype.de).

## Setup
To test the webapp with sqlite3 backend just clone the repository
and run the django development server
```
git clone https://github.com/janekg89/flutype_webapp.git
mkvirtualenv flutype_webapp
(flutype_webapp) pip install -r requirements.txt
(flutype_webapp) python manage.py runserver
```

## Testing
Tests are run via
```
(flutype_webapp) python manage.py test
```

Running the unittests requires `phantomjs` which can be installed via the
following the instructions on
https://www.vultr.com/docs/how-to-install-phantomjs-on-ubuntu-16-04
```
sudo apt-get install build-essential chrpath libssl-dev libxft-dev libfreetype6-dev libfreetype6 libfontconfig1-dev libfontconfig1 -y
sudo wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
sudo tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2 -C /usr/local/share/
sudo ln -s /usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/
phantomjs --version
```


## Container & Deployment
For testing and deployment gunicorn and docker scripts are available. These are still experimental.

### gunicorn
To test if gunicorn can serve the WSGI application use
```
(flutype_webapp) gunicorn --bind 0.0.0.0:8000 flutype_webapp.wsgi:application
```
This will not serve the static files but check if the WSGI django works with gunicorn,
which is close to the actual deployment setup.

Gunicorn can be installed via
```
sudo apt-get install gunicorn
```

### Docker
Install `docker-ce` and `docker-compose` on the system.

Run the app via
```
docker-compose up
```

```
cd flutype_webapp
./docker-entrypoint.sh
```

&copy; 2017 flutype