#!/bin/sh
python manage.py runfcgi method=prefork host=127.0.0.1 port=9001 pidfile=jwter.fcgi.pid daemonize=False
