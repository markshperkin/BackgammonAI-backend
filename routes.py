# API endpoints
import random
from flask import Blueprint, request, jsonify, Response, Flask
from game import Backgammon
import json
import heapq
from random_ai import Rplay_ai_move
app = Flask(__name__)

from minimax import minimax_move, event_queue


# create a blueprint instead of directly using `app`
game_routes = Blueprint("game_routes", __name__)
# create a game
game = Backgammon()

# start a new game
@game_routes.route('/api/game/start', methods=['POST'])
def start_game():
    global game
    data = request.get_json() or {}
    ai_type = data.get("aiType", "random")
    game = Backgammon()
    game.current_player = random.choice([1, -1])
    game.roll_dice()
    if ai_type == "random":
        game.ai_move_fn = Rplay_ai_move
    elif ai_type == "minimax":
        game.ai_move_fn = minimax_move
    else:
        game.ai_move_fun = Rplay_ai_move
    return jsonify(game.get_board_state())

# roll dice
@game_routes.route('/api/game/roll-dice', methods=['GET'])
def roll_dice():
    dice = game.roll_dice()
    print("dice", dice, "moves remaining:", game.moves_remaining)
    return jsonify({"dice": dice, "moves_remaining": game.moves_remaining})

# user make move
@game_routes.route('/api/game/move', methods=['POST'])
def move():
    """Processes a player's move."""
    data = request.json
    start = data.get('start')
    end = data.get('end')

    if game.make_move(start, end):
        return jsonify(game.get_board_state())
    else:
        return jsonify({"error": "Invalid move"}), 400

# get game state
@game_routes.route('/api/game/state', methods=['GET'])
def get_state():
    """Returns the current game state."""
    return jsonify(game.get_board_state())

# get valid moves
@game_routes.route('/api/game/valid-moves', methods=['POST'])
def valid_moves():
    data = request.json
    start = data.get('start')
    if start is None:
        return jsonify({"error": "Missing 'start' parameter"}), 400
    valid_moves = game.get_valid_moves(start)
    return jsonify({"valid_moves": valid_moves})

# AI agent make move
@game_routes.route('/api/game/ai-move', methods=['POST'])
def ai_move():

    # check that its AIs turn (black)
    if game.current_player != -1:
        return jsonify({"error": "Not AI's turn"}), 400

    new_state = game.ai_move_fn(game, delay=1.0)
    print("current board state:", game.get_board_state())

    return jsonify(new_state)

_depth_map = {}    # node_id → depth
_top_heaps = {}    # depth → min‑heap of (score, node_id)

# function to decide if to emite data to the front end.
# uses heaps for each level or depth to find the best node with the best score to send.
# cap is 10 nodes per level.
def _should_emit(event):
    # determine this node's depth from its parent
    parent = event.get('parent')
    parent_depth = _depth_map.get(parent, -1)
    depth = parent_depth + 1
    _depth_map[event['id']] = depth

    heap = _top_heaps.setdefault(depth, [])
    if len(heap) < 10:
        heapq.heappush(heap, (event['score'], event['id']))
        return True

    # if this event beats the smallest top‑10 score at this depth
    if event['score'] > heap[0][0]:
        heapq.heapreplace(heap, (event['score'], event['id']))
        return True

    return False

# send a stream of data (search graph) to the front end
@game_routes.route('/stream')
def stream_events():
    """
    Server‑Sent Events endpoint that streams instrumentation events
    from the minimax event_queue to the frontend in real time.
    """
    def event_generator():
        while True:
            event = event_queue.get()   # blocks until an event is available
            # print(f"[SSE ▶] Sending event: {event}")   # ← debug print
            # SSE requires 'data: ' prefix and a blank line after each event
            yield f"data: {json.dumps(event)}\n\n"

    # Disable HTTP caching so proxies don’t buffer
    headers = {
      'Cache-Control': 'no-cache',
      'X-Accel-Buffering': 'no'   # if you’re behind nginx
    }
    return Response(event_generator(), headers=headers,
                    mimetype='text/event-stream')
