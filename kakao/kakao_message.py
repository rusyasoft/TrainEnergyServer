#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, Response
from gevent.wsgi import WSGIServer
import json

FROM = ["녹동에서","소태에서","학동증심사입구에서","남광주에서","문화전당에서","금남로4가에서","금남로5가에서"]

app = Flask(__name__)

@app.route("/keyboard", methods=['GET', 'POST'])
def keyboard_processor():
    if request.method == 'POST':
        print 'POST request'
    else:
        print 'GET request'
    #return u"{'type':'buttons','buttons':['안녕하세요..', 'choice2', 'choice3']}"
    return '{"type":"buttons", "buttons":["start bot"]}'
    #return '{"type":"buttons", "buttons":""}'

@app.route("/message", methods=['GET', 'POST'])
def message_processor():
    if request.method == 'POST':
        print 'POST request', request.data
        
    else:
        print 'GET request'
    #return u"{'type':'buttons','buttons':['안녕하세요..', 'choice2', 'choice3']}"
    #return '{"message": {"text": "We will consider you request, He-he-he !" } }'
    show_buttons = json.dumps({
                                        "message": {
                                        "text": u"어디에서 출발하시나요? 옆으로 쓸어 넘겨 출발지를 찾아보세요."
                                    },
                                        "keyboard": {
                                                        "type": "buttons",
                                                        "buttons": FROM
                                    }
                        })
    return Response(show_buttons, mimetype='application/json')


if __name__ == '__main__':
    http_server= WSGIServer(('', 5000), app)
    http_server.serve_forever()
