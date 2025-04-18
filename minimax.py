import time
from collections import Counter

from gameForAI import (
    apply_pip_move_inplace,
    undo_pip_move_inplace,
    apply_roll_inplace,
    undo_roll_inplace,
    get_rolls_and_probs
)

def evaluate_board(game):
    white_dist = 0
    black_dist = 0
    for idx, count in enumerate(game.board):
        if count > 0:
            white_dist += idx * count
        elif count < 0:
            black_dist += (23 - idx) * abs(count)
    BAR_PENALTY = 30
    white_dist += game.bar_white * BAR_PENALTY
    black_dist += game.bar_black * BAR_PENALTY
    BARE_OFF_BOOST = 30
    white_dist -= game.borne_off_white * BARE_OFF_BOOST
    black_dist -= game.borne_off_black * BARE_OFF_BOOST


    return white_dist - black_dist

def expectiminimax_ab(state, depth, alpha, beta):
    """
    minimax with alpha beta pruning modified to take into account double rolls (same dice result in four moves)
    identical pip values only expanded once per turn. reduces complexity.
    """
    # terminal states (base case)
    if depth == 0 or state.game_over:
        return evaluate_board(state)

    # decision node/s
    if state.moves_remaining:
        # fix infinity score, caused by graph leafs do not have legal moves, probability part never executed. 
        legal = [
            (s, e, d, mt)
            for (s, e, d, mt) in state.get_all_available_moves()
            if d in state.moves_remaining
        ]
        if not legal:
            # no pip‑moves available -> treat as probability node
            total = 0.0
            for roll, prob in get_rolls_and_probs():
                rec = apply_roll_inplace(state, roll)
                val = expectiminimax_ab(state, depth - 1, alpha, beta)
                undo_roll_inplace(state, rec)
                total += prob * val
            return total
        pip_counts = Counter(state.moves_remaining)

        # MAX node (black) - agent
        if state.current_player == -1:
            value = -float("inf")
            for pip_value in pip_counts:
                for start, end, die, _ in state.get_all_available_moves():
                    if die != pip_value:
                        continue

                    rec = apply_pip_move_inplace(state, start, end)
                    val = expectiminimax_ab(state, depth, alpha, beta)
                    undo_pip_move_inplace(state, rec)

                    # alpha beta pruning part
                    if val > value:
                        value = val
                    if value > alpha:
                        alpha = value
                    if alpha >= beta:
                        break
                if alpha >= beta:
                    break
            return value

        # MIN node (white) - user
        else:
            value = float("inf")
            for pip_value in pip_counts:
                for start, end, die, _ in state.get_all_available_moves():
                    if die != pip_value:
                        continue

                    rec = apply_pip_move_inplace(state, start, end)
                    val = expectiminimax_ab(state, depth, alpha, beta)
                    undo_pip_move_inplace(state, rec)

                    # alpha beta pruning part
                    if val < value:
                        value = val
                    if value < beta:
                        beta = value
                    if alpha >= beta:
                        break
                if alpha >= beta:
                    break
            return value

    # probability node
    total = 0.0
    for roll, prob in get_rolls_and_probs():
        rec = apply_roll_inplace(state, roll)
        val = expectiminimax_ab(state, depth - 1, alpha, beta)
        undo_roll_inplace(state, rec)
        total += prob * val

    return total

def minimax_move(game, delay=0.0):
    """
    executes the best move going from last moves to get better strategy (focus on farthest pips)
    using expectiminimax_ab to look ahead 2 plays.
    """
    depth = 2
    startT = time.time()

    if game.current_player != -1 or game.game_over:
        return game.get_board_state()

    available = game.get_all_available_moves()
    if len(available) == 1:
        time.sleep(delay)
        s, e, _, _ = available[0]
        game.make_move(s, e)
        return game.get_board_state()

    best_score = -float("inf")
    best_move = None
    seen = set()

    # loop to get the best move, going in reverse
    for start, end, _, _ in reversed(available):
        if (start, end) in seen:
            continue
        seen.add((start, end))
        print("simulating this move:", start, end)
        rec = apply_pip_move_inplace(game, start, end)
        score = expectiminimax_ab(game, depth, -float("inf"), float("inf"))
        undo_pip_move_inplace(game, rec)
        print("score:", score)
        if score > best_score:
            best_score = score
            best_move = (start, end)

    # execute chosen move
    if best_move:
        game.make_move(*best_move)

    endT = time.time()
    print("best move:", best_move,
          "score:", best_score,
          "time:", endT - startT)
    return game.get_board_state()
