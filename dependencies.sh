#!/bin/sh
# The file used to install the dependencies (apk or pip)
echo "Installing the dependencies..."
#apk add --update --no-cache bash gettext build-base jpeg-dev nginx python3-dev openldap-dev libressl-dev musl-dev libffi-dev postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev vim openssl-dev py3-lxml py3-pyldap

# Basic dependencies
apk add --upgrade --no-cache bash gettext build-base python3-dev gcc vim

# Pillow
apk add --upgrade --no-cache jpeg-dev zlib-dev

echo "Upgrading the pip..."
pip install --upgrade pip

echo "Installing the requiremed pypi packges..."
pip install -r `dirname $0`/requirements.txt
