# main flask app. entry point of the backend. 
import os
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

# init flask app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

from routes import game_routes
app.register_blueprint(game_routes)


print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(f"   {rule}")

@app.route('/')
def home():
    return {"message": "Backgammon API is running!"}

# Run the server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    # host 0.0.0.0 so it listens on all interfaces
    app.run(host="0.0.0.0", port=port, threaded=True)
    socketio.run(app, debug=True)

