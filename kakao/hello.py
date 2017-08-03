#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request
from gevent.wsgi import WSGIServer

app = Flask(__name__)

@app.route("/keyboard", methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        print 'POST request'
    else:
        print 'GET request'
    #return u"{'type':'buttons','buttons':['안녕하세요..', 'choice2', 'choice3']}"
    return '{"type":"buttons", "buttons":["ch1","ch2","ch3" ]}'


if __name__ == '__main__':
    http_server= WSGIServer(('', 5000), app)
    http_server.serve_forever()
