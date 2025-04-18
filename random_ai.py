import time
import random

def Rplay_ai_move(game, delay=1.0):
    if game.current_player != -1 or game.game_over:
        return game.get_board_state()
    
    available_moves = game.get_all_available_moves()
    if not available_moves:
        return game.get_board_state()

    chosen_move = random.choice(available_moves)
    start, end, _, _ = chosen_move
    
    # have delay to simulate "AI" thinking as random is very fast
    time.sleep(delay)
    
    game.make_move(start, end)
    print("AI move executed:", chosen_move)
    
    if not game.moves_remaining or not game.can_make_any_move():
        return game.get_board_state()
    
    return game.get_board_state()
