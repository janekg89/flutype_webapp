##############################################################################
# Dockerfile
##############################################################################
# Dockerfile for running the webapp in a container.
# The container can be build and run via:
#
#   docker build -t matthiaskoenig/flutype_webapp . && docker run -it -p 8000:8000 matthiaskoenig/flutype_webapp
#
##############################################################################
FROM python:3
MAINTAINER Matthias Koenig <konigmatt@googlemail.com>

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

# Install latest flutype_analysis
RUN pip install git+https://github.com/matthiaskoenig/flutype-analysis.git@develop

CMD ["echo", "*Finished building containter*"]
# Run tests
# WORKDIR /usr/src/app/flutype_webapp
# RUN python manage.py test

# EXPOSE 8000
# WORKDIR /code
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# CMD ["python", "manage.py", "test"]