from app import app, socketio

PORT = 8080

if __name__ == "__main__":
    print "Server is listening to port {}".format(PORT)
    socketio.run(app, port=PORT)
