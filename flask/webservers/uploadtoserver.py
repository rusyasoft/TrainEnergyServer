from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

import cgi

class StoreHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['content-length'])
        print 'File length = ', length
        if length > 10000000:
            print "file to big"
            #self.send_response("file to big")
            read = 0
            while read < length:
                read += len(self.rfile.read(min(66556, length - read)))
            self.respond("file to big")
            return

        else:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                         'CONTENT_TYPE':self.headers['Content-Type'],
                         })
            filename = form['file'].filename
            data = form['file'].file.read()
            #open("/tmp/%s"%filename, "wb").write(data)
            open("/home/rustam/python_poligon/webservers/excelsrc/%s"%filename, "wb").write(data)
            print self.headers['content-length']
            self.respond("uploaded %s, thanks"%filename)

    def do_GET(self):
        response = """
        <html><body>
        <form enctype="multipart/form-data" method="post">
        <p>File: <input type="file" name="file"></p>
        <p><input type="submit" value="Upload"></p>
        </form>
        </body></html>
        """        

        self.respond(response)

    def respond(self, response, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response)  


server = HTTPServer(('', 3002), StoreHandler)
server.serve_forever()


