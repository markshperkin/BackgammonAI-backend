import time
from collections import Counter
import uuid
import queue
from collections import defaultdict

from gameForAI import (
    apply_pip_move_inplace,
    undo_pip_move_inplace,
    apply_roll_inplace,
    undo_roll_inplace,
    get_rolls_and_probs
)
# queue for emiting the events, maps for chance nodes, two min moves nodes.
event_queue = queue.Queue()
childrenChance = defaultdict(list)
childrenMIN1 = defaultdict(list)
childrenMIN2 = defaultdict(list)
send_limit = 0
agent = None


# function to emit the events to api
def emit_event(node_id, parent_id, move, score, tree_depth, current_player, remaining, ischance):
    event = {
        'id': node_id,
        'parent': parent_id,
        'move': move,
        'score': score,
        'current_player': current_player,
        'ischance': ischance
    }
    global send_limit

    # print("emiting this data:", event)

    # collects and sorts the levels of the tree depends on the remaining moves. 
    # displays 3 chance nodes, 2 lowest score min and for each one more move of min. max 200 nodes per move
    if send_limit < 200:
        if remaining == 4:
            if current_player == -1 and tree_depth < 4:
                event_queue.put(event)
                send_limit += 1
            elif current_player == 1 and tree_depth < 7:
                if score is not None:
                    if tree_depth == 4:
                        childrenChance[parent_id].append(event)
                    elif tree_depth == 5 and parent_id in childrenChance:
                        childrenMIN1[parent_id].append(event)
                    elif tree_depth == 6:
                        childrenMIN2[parent_id].append(event)
                    if len(childrenChance[parent_id]) == 21:
                        top5 = sorted(childrenChance[parent_id], key=lambda e: e['score'])[:3]
                        for ev in top5:
                            event_queue.put(ev)
                            send_limit += 1
                            m1 = sorted(childrenMIN1.get(ev['id'], []), key=lambda e: e['score'])[:2]
                            for ev1 in m1:
                                event_queue.put(ev1)
                                send_limit += 1
                                m2 = sorted(childrenMIN2.get(ev1['id'], []), key=lambda e: e['score'])[:1]
                                for ev2 in m2:
                                    event_queue.put(ev2)
                                    send_limit += 1
                                childrenMIN2.pop(ev['id'], None)
                            childrenMIN1.pop(ev['id'], None)

                        del childrenChance[parent_id]

        elif remaining == 3:
            if current_player == -1 and tree_depth < 3:
                event_queue.put(event)
                send_limit += 1
            elif current_player == 1 and tree_depth < 6:
                if score is not None:
                    if tree_depth == 3:
                        childrenChance[parent_id].append(event)
                    elif tree_depth == 4 and parent_id in childrenChance:
                        childrenMIN1[parent_id].append(event)

                    elif tree_depth == 5:
                        childrenMIN2[parent_id].append(event)
                    if len(childrenChance[parent_id]) == 21:
                        top5 = sorted(childrenChance[parent_id], key=lambda e: e['score'])[:3]
                        for ev in top5:
                            event_queue.put(ev)
                            send_limit += 1
                            m1 = sorted(childrenMIN1.get(ev['id'], []), key=lambda e: e['score'])[:2]
                            for ev1 in m1:
                                event_queue.put(ev1)
                                send_limit += 1
                                m2 = sorted(childrenMIN2.get(ev1['id'], []), key=lambda e: e['score'])[:1]
                                for ev2 in m2:
                                    event_queue.put(ev2)
                                    send_limit += 1
                                childrenMIN2.pop(ev['id'], None)
                            childrenMIN1.pop(ev['id'], None)

                        del childrenChance[parent_id]

        elif remaining == 2:
            if current_player == -1 and tree_depth < 2:
                event_queue.put(event)
                send_limit += 1
            elif current_player == 1 and tree_depth < 5:
                if score is not None:
                    if tree_depth == 2:
                        childrenChance[parent_id].append(event)
                    elif tree_depth == 3 and parent_id in childrenChance:
                        childrenMIN1[parent_id].append(event)

                    elif tree_depth == 4:
                        childrenMIN2[parent_id].append(event)
                    if len(childrenChance[parent_id]) == 21:
                        top5 = sorted(childrenChance[parent_id], key=lambda e: e['score'])[:3]
                        for ev in top5:
                            event_queue.put(ev)
                            send_limit += 1
                            m1 = sorted(childrenMIN1.get(ev['id'], []), key=lambda e: e['score'])[:2]
                            for ev1 in m1:
                                event_queue.put(ev1)
                                send_limit += 1
                                m2 = sorted(childrenMIN2.get(ev1['id'], []), key=lambda e: e['score'])[:1]
                                for ev2 in m2:
                                    event_queue.put(ev2)
                                    send_limit += 1
                                childrenMIN2.pop(ev['id'], None)
                            childrenMIN1.pop(ev['id'], None)

                        del childrenChance[parent_id]

        elif remaining == 1:
            if current_player == -1 and tree_depth < 1:
                event_queue.put(event)
                send_limit += 1
            elif current_player == 1 and tree_depth < 4:
                if score is not None:
                    if tree_depth == 1:
                        childrenChance[parent_id].append(event)
                    elif tree_depth == 2 and parent_id in childrenChance:
                        childrenMIN1[parent_id].append(event)

                    elif tree_depth == 3:
                        childrenMIN2[parent_id].append(event)
                    if len(childrenChance[parent_id]) == 21:
                        top5 = sorted(childrenChance[parent_id], key=lambda e: e['score'])[:3]
                        for ev in top5:
                            event_queue.put(ev)
                            send_limit += 1
                            m1 = sorted(childrenMIN1.get(ev['id'], []), key=lambda e: e['score'])[:2]
                            for ev1 in m1:
                                event_queue.put(ev1)
                                send_limit += 1
                                m2 = sorted(childrenMIN2.get(ev1['id'], []), key=lambda e: e['score'])[:1]
                                for ev2 in m2:
                                    event_queue.put(ev2)
                                    send_limit += 1
                                childrenMIN2.pop(ev['id'], None)
                            childrenMIN1.pop(ev['id'], None)
                        del childrenChance[parent_id]

def evaluate_board(game):
    white_dist = 0
    black_dist = 0
    dice_balance = 0
    BAR_PENALTY = 30
    BARE_OFF_BOOST = 30

    for idx, count in enumerate(game.board):
        if count > 0:
            white_dist += idx * count
            if count >= 2:
                white_dist -= 3
        elif count < 0:
            black_dist += (23 - idx) * abs(count)
            if count <= 2:
                black_dist -= 3
                
    for die in game.moves_remaining:
        dice_balance += die
        

    white_dist += game.bar_white * BAR_PENALTY
    black_dist += game.bar_black * BAR_PENALTY
    
    white_dist -= game.borne_off_white * BARE_OFF_BOOST
    black_dist -= game.borne_off_black * BARE_OFF_BOOST

    if game.current_player == -1:
        black_dist += dice_balance / 2
        return white_dist - black_dist
    else:
        white_dist += dice_balance / 2
        return black_dist - white_dist

def expectiminimax_ab(state, depth, alpha, beta, parent_id, last_move, tree_depth, remaining, ischance):
    """
    minimax with alpha beta pruning modified to take into account double rolls (same dice result in four moves)
    identical pip values only expanded once per turn. reduces complexity.
    incoperated event transmition of node if, parent id, last move, score each time function returns.
    """
    total = 0.0

    # unique id for each node.
    node_id = uuid.uuid4().hex
    if last_move is not None:
        emit_event(node_id, parent_id, last_move, None, tree_depth, state.current_player, remaining, ischance)

    # terminal states (base case)
    if depth == 0 or state.game_over:
        score = evaluate_board(state)
        total = score

    # decision node/s
    elif state.moves_remaining:
        # fix infinity score, caused by graph leafs do not have legal moves, probability part never executed. 
        legal = [
            (s, e, d, mt)
            for (s, e, d, mt) in state.get_all_available_moves()
            if d in state.moves_remaining
        ]
        if not legal:
            # no pip moves available -> treat as probability node
            for roll, prob in get_rolls_and_probs():
                rec = apply_roll_inplace(state, roll)
                val = expectiminimax_ab(state, depth - 1, alpha, beta, node_id, roll, tree_depth+1, remaining, ischance=True) # pass in roll because its about probability
                undo_roll_inplace(state, rec)
                total += prob * val

        else:
            pip_counts = Counter(state.moves_remaining)
            # MAX node (black) - agent
            if state.current_player == agent:
                value = -float("inf")
                for pip_value in pip_counts:
                    for start, end, die, _ in state.get_all_available_moves():
                        if die != pip_value:
                            continue

                        rec = apply_pip_move_inplace(state, start, end)
                        val = expectiminimax_ab(state, depth, alpha, beta, node_id, (start, end), tree_depth+1, remaining, ischance=False)
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

                total = value

            # MIN node (white) - user
            else:
                value = float("inf")
                for pip_value in pip_counts:
                    for start, end, die, _ in state.get_all_available_moves():
                        if die != pip_value:
                            continue

                        rec = apply_pip_move_inplace(state, start, end)
                        val = expectiminimax_ab(state, depth, alpha, beta, node_id, (start, end), tree_depth+1, remaining, ischance=False)
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

                total = value

    # probability node
    else:
        for roll, prob in get_rolls_and_probs():
            rec = apply_roll_inplace(state, roll)
            val = expectiminimax_ab(state, depth - 1, alpha, beta, node_id, roll, tree_depth+1, remaining, ischance=True) # pass in roll because its about probability
            undo_roll_inplace(state, rec)
            total += prob * val

    if last_move is not None:
        emit_event(node_id, parent_id, last_move, total, tree_depth, state.current_player, remaining, ischance)
    return total

def minimax_move(game, delay=0.0):
    """
    executes the best move going from last moves to get better strategy (focus on farthest pips)
    using expectiminimax_ab to look ahead 2 plays.
    """
    global send_limit
    depth = 2
    startT = time.time()
    global agent
    agent = game.current_player

    if game.game_over:
        return game.get_board_state()

    available = game.get_all_available_moves()
    if len(available) == 1:
        s, e, _, _ = available[0]
        game.make_move(s, e)
        return game.get_board_state()

    best_score = -float("inf")
    best_move = None
    seen = set()

    # loop to get the best move, going in reverse
    for start, end, _, _ in reversed(available):
        remaining = len(game.moves_remaining)
        root_id = uuid.uuid4().hex

        if (start, end) in seen:
            continue
        seen.add((start, end))
        print("simulating this move:", start, end)
        rec = apply_pip_move_inplace(game, start, end)
        score = expectiminimax_ab(game, depth, -float("inf"), float("inf"), parent_id = root_id, last_move=(start, end), tree_depth=0, remaining=remaining, ischance=False)
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
    print(send_limit)
    send_limit = 0
    return game.get_board_state()