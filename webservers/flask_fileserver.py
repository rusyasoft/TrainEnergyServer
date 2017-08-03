from flask import Flask, request, send_from_directory, render_template
from gevent.wsgi import WSGIServer

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='') #'/home/rustam/python_poligon/webservers/')

@app.route('/download/<path:path>')
def send_js(path):
    print "triggered1"
    return send_from_directory('download', path)

@app.route('/')
def root():
    print 'triggered 2'
    #return send_from_directory('/', 'index.html')
    return app.send_static_file('index.html')
    #return render_template("index.html")

if __name__ == "__main__":
    #app.run(
    #    host="0.0.0.0",
    #    port=int("80")
    #)
    http_server = WSGIServer( ('', 80) , app)
    http_server.serve_forever()



