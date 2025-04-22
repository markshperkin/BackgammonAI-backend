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


print("▶ Registered routes:")
for rule in app.url_map.iter_rules():
    print(f"   {rule}")

@app.route('/')
def home():
    return {"message": "Backgammon API is running!"}

# Run the server
if __name__ == '__main__':
    socketio.run(app, debug=True)

