##############################################################################
# Dockerfile
##############################################################################
# Dockerfile for running the webapp in a container.
# The container can be build and run via:
#
#   docker build -t matthiaskoenig/flutype_webapp . && docker run -it -p 8000:8000 matthiaskoenig/flutype_webapp
#
##############################################################################
FROM python:2.7.13
MAINTAINER Matthias Koenig <konigmatt@googlemail.com>

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

# Install latest flutype_analysis
RUN pip install git+https://github.com/matthiaskoenig/flutype-analysis.git@master

# Run tests
# WORKDIR /usr/src/app/flutype_webapp
# RUN python manage.py test

EXPOSE 8000
WORKDIR /usr/src/app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]