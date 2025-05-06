from functools import partial
import random
from flask import Blueprint, request, jsonify, Response
from game import Backgammon
import json
from random_ai import Rplay_ai_move
from furthest_first import FFA_ai_move
from closest_first import CFA_ai_move
from minimax import minimax_move, event_queue
from TD import TD0_move

game_routes = Blueprint("game_routes", __name__)
game = Backgammon()

# find the specific ai move function
def lookup_ai(ai_type: str):
    """
    Return the correct AI‐move function (or a partial) for a given ai_type,
    and print a startup banner.
    """
    if ai_type == "random":
        print("---- starting random agent ----")
        return Rplay_ai_move
    
    elif ai_type == "FFA":
        print("---- starting FFA agent ----")
        return FFA_ai_move
    
    elif ai_type == "CFA":
        print("---- starting CFA agent ----")
        return CFA_ai_move

    elif ai_type == "minimax":
        print("---- starting minimax agent ----")
        return minimax_move

    elif ai_type.startswith("TD"):
        print(f"---- starting {ai_type} agent ----")
        return partial(TD0_move, TD_variant=ai_type)

    else:
        print("---- starting random agent ----")
        return Rplay_ai_move

# start a new game
@game_routes.route('/api/game/start', methods=['POST'])
def start_game():
    global game
    data    = request.get_json() or {}
    ai_type = data.get("aiType", "random")

    game = Backgammon()
    game.mode = "human-vs-ai"
    game.current_player = random.choice([1, -1])
    game.roll_dice()

    game.ai_move_fn = lookup_ai(ai_type)

    return jsonify(game.get_board_state())

# start a new match
@game_routes.route('/api/game/start-match', methods=['POST'])
def start_match():
    global game
    data  = request.get_json() or {}
    black = data.get("blackAiType", "random")
    white = data.get("whiteAiType", "random")

    game = Backgammon()
    game.mode = "ai-vs-ai"
    game.current_player = random.choice([1, -1])
    game.roll_dice()

    game.ai_black_fn = lookup_ai(black)
    game.ai_white_fn = lookup_ai(white)

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
    # AI vs AI
    if getattr(game, "mode", None) == "ai-vs-ai":
        if game.current_player == 1 and game.ai_black_fn:
            new_state = game.ai_black_fn(game, delay=1.0)
        elif game.current_player == -1 and game.ai_white_fn:
            new_state = game.ai_white_fn(game, delay=1.0)
        else:
            return jsonify({"error":"Not AI’s turn"}), 400

    # human vs AI
    else:
        if not hasattr(game, "ai_move_fn"):
            return jsonify({"error":"AI not bound"}), 400
        new_state = game.ai_move_fn(game, delay=1.0)

    return jsonify(new_state)


# send a stream of data (search graph) to the front end
@game_routes.route('/stream')
def stream_events():
    """
    server Sent Events endpoint that streams instrumentation events
    from the minimax event_queue to the frontend in real time.
    """
    def event_generator():

        while True:
            event = event_queue.get()
            # print(f"[SSE] Sending event: {event}")
            
            yield f"data: {json.dumps(event)}\n\n"

    headers = {
      'Cache-Control': 'no-cache',
      'X-Accel-Buffering': 'no'
    }
    return Response(event_generator(), headers=headers,
                    mimetype='text/event-stream')



