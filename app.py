# main flask app. entry point of the backend. 
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

# init flask app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

from routes import game_routes
app.register_blueprint(game_routes)

@app.route('/')
def home():
    return {"message": "Backgammon API is running!"}

# Run the server
if __name__ == '__main__':
    socketio.run(app, debug=True)

