import csv
import random
from functools import partial

from game import Backgammon
from random_ai import Rplay_ai_move
from furthest_first import FFA_ai_move
from closest_first import CFA_ai_move
from minimax import minimax_move
from TD import TD0_move



AGENTS = {
    "random":         Rplay_ai_move,
    "CFA":            CFA_ai_move,
    "FFA":            FFA_ai_move,

    # "minimax":        minimax_move,

    # "TD0v1e_4000":     partial(TD0_move, TD_variant="TD0v1e_4000"),
    # "TD0v1e_10000":     partial(TD0_move, TD_variant="TD0v1e_10000"),
    "TD0v1e_35000":     partial(TD0_move, TD_variant="TD0v1e_35000"),

    # "TD0v2e_4000":     partial(TD0_move, TD_variant="TD0v2e_4000"),
    # "TD0v2e_10000":     partial(TD0_move, TD_variant="TD0v2e_10000"),
    # "TD0v2e_35000":     partial(TD0_move, TD_variant="TD0v2e_35000"),

    # "TDLv1e_4000":     partial(TD0_move, TD_variant="TDLv1e_4000"),
    # "TDLv1e_10000":     partial(TD0_move, TD_variant="TDLv1e_10000"),
    "TDLv1e_35000":     partial(TD0_move, TD_variant="TDLv1e_35000"),

    # "MCV1e_4000":     partial(TD0_move, TD_variant="MCV1e_4000"),
    # "MCV1e_10000":     partial(TD0_move, TD_variant="MCV1e_10000"),
    "MCV1e_35000":     partial(TD0_move, TD_variant="MCV1e_35000"),

}

NUM_GAMES   = 1000
OUTPUT_FILE = "All.csv"


def play_match(fn_black, fn_white):
    game = Backgammon()
    game.current_player = random.choice([1, -1])
    game.roll_dice()

    game.ai_black_fn = fn_black
    game.ai_white_fn = fn_white

    while not game.game_over:
        if game.current_player == 1:
            game.ai_white_fn(game, delay=0)
        else:
            game.ai_black_fn(game, delay=0)

    return game.game_over


def main():
    names = list(AGENTS.keys())
    n     = len(names)

    results = [[None]*n for _ in range(n)]
    for i in range(n):
        results[i][i] = "-"  # diagonal

    for i in range(n):
        for j in range(i+1, n):
            name_i, name_j = names[i], names[j]
            fn_i, fn_j     = AGENTS[name_i], AGENTS[name_j]

            wins_i = wins_j = 0
            for _ in range(NUM_GAMES):
                # randomly choose who plays
                if random.choice([True, False]):
                    # fn_i is BLACK, fn_j is WHITE
                    outcome = play_match(fn_i, fn_j)
                    if outcome == 1:
                        wins_j += 1
                    else:
                        wins_i += 1
                else:
                    outcome = play_match(fn_j, fn_i)
                    if outcome == 1:
                        wins_i += 1
                    else:
                        wins_j += 1

            results[i][j] = f'({wins_i},{wins_j})'
            results[j][i] = f'({wins_j},{wins_i})'


    with open(OUTPUT_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([""] + names)
        for i, name in enumerate(names):
            writer.writerow([name] + results[i])

    print(f"round robin matrix written to {OUTPUT_FILE}")




if __name__ == "__main__":
    main()
