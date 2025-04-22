import copy
from game import Backgammon

"""
instead of coping the board each play, I modify it using recoreded board. 
significatly speeds up the search, making minimax usable.
"""
def apply_pip_move_inplace(state: Backgammon, start: int, end: int) -> dict:
    """
    mutate the state by applying one move wihtout switching player or rolling the dice
    """
    # find the move tuple
    move = next((m for m in state.get_all_available_moves() if m[0] == start and m[1] == end), None)
    if move is None:
        raise ValueError(f"Illegal move ({start}->{end}) for this state")
    d, move_type = move[2], move[3]

    # record board state
    rec = {
        "start": start,
        "end": end,
        "pip": d,
        "move_type": move_type,
        "orig_bar_white":         state.bar_white,
        "orig_bar_black":         state.bar_black,
        "orig_borne_off_white":   state.borne_off_white,
        "orig_borne_off_black":   state.borne_off_black,
    }
    # in case of bared off pips (in jail)
    if 0 <= start < 24:
        rec["orig_start_val"] = state.board[start]
    if 0 <= end < 24:
        rec["orig_end_val"] = state.board[end]

    # apply the move
    if move_type == "re-entry":
        if state.current_player == 1:
            if state.board[end] < 0:
                state.board[end] = 0
                state.bar_black += 1
            state.board[end] += 1
            state.bar_white -= 1
        else:
            if state.board[end] > 0:
                state.board[end] = 0
                state.bar_white += 1
            state.board[end] -= 1
            state.bar_black -= 1

    elif move_type == "bear_off":
        if state.current_player == 1:
            state.board[start] -= 1
            state.borne_off_white += 1
        else:
            state.board[start] += 1
            state.borne_off_black += 1

    elif move_type == "normal":
        piece = 1 if state.current_player == 1 else -1
        if state.current_player == 1 and state.board[end] == -1:
            state.board[end] = 0
            state.bar_black += 1
        elif state.current_player == -1 and state.board[end] == 1:
            state.board[end] = 0
            state.bar_white += 1
        state.board[end] += piece
        state.board[start] -= piece

    # consume the pip
    state.moves_remaining.remove(d)
    return rec

def undo_pip_move_inplace(state: Backgammon, rec: dict):
    """
    undo a single move applied by apply_pip_move_inplace.
    """
    
    if "orig_start_val" in rec:
        state.board[rec["start"]] = rec["orig_start_val"]
    if "orig_end_val" in rec:
        state.board[rec["end"]] = rec["orig_end_val"]
    state.bar_white                   = rec["orig_bar_white"]
    state.bar_black                   = rec["orig_bar_black"]
    state.borne_off_white             = rec["orig_borne_off_white"]
    state.borne_off_black             = rec["orig_borne_off_black"]
    # restore the consumed pip
    state.moves_remaining.append(rec["pip"])


def apply_roll_inplace(state: Backgammon, roll: tuple[int,int]) -> dict:
    """
    mutate the state by flipping the turn and setting the dice and moves_remaining
    """
    rec = {
        "orig_current_player": state.current_player,
        "orig_dice":           state.dice,
        "orig_moves_remaining": state.moves_remaining.copy(),
    }
    # flip turn
    state.current_player *= -1
    state.dice = roll
    d1, d2 = roll
    state.moves_remaining = [d1, d2] if d1 != d2 else [d1] * 4
    return rec

def undo_roll_inplace(state: Backgammon, rec: dict):
    """
    undo a roll applied by apply_roll_inplace.
    """
    state.current_player    = rec["orig_current_player"]
    state.dice              = rec["orig_dice"]
    state.moves_remaining   = rec["orig_moves_remaining"]


def get_rolls_and_probs() -> list[tuple[tuple[int,int], float]]:
    """
    dice outcomes (i <= j), 21 combos, each with probability 1/21.
    """
    combos = [(i, j) for i in range(1, 7) for j in range(i, 7)]
    p = 1 / len(combos)
    return [(roll, p) for roll in combos]


def simulate_full_turn(state: Backgammon, roll: tuple[int,int], moves: list[tuple[int,int]]):
    """
    simulate one full turn: flips player, sets dice, then applies each move
    """
    g = copy.deepcopy(state)
    # apply the roll in place on the copy
    rec_roll = apply_roll_inplace(g, roll)
    for start, end in moves:
        rec_move = apply_pip_move_inplace(g, start, end)
        # no undo here, this is on the copy
    return g


def generate_pip_successors(state: Backgammon):
    """
    return list of (new_state, (start,end)) for each legal single pip move,
    """
    successors = []
    for start, end, _, _ in state.get_all_available_moves():
        rec = apply_pip_move_inplace(state, start, end)
        successors.append((copy.deepcopy(state), (start, end)))
        undo_pip_move_inplace(state, rec)
    return successors
