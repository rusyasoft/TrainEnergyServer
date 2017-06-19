from flask import Flask, request
app = Flask(__name__)

@app.route("/", methods=['POST'])
def hellos():

    data = request.data
    if data != None:
        print "recevied post data: ", data
    
    return ("Hello World!\n", 200)


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("5000")
    )
