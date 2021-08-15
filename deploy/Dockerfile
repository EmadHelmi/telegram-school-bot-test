FROM school-bot/core AS builder

# set working directory
WORKDIR /code

# install dependencies
COPY deploy/requirements.txt /code/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt -q
RUN apt-get -y update

WORKDIR /code/school_bot