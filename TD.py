import time
import copy
import torch
from TDGammonNet import TDGammonNetV1, TDGammonNetV2
from gameForAI import get_board_features, generate_pip_successors




def TD0_move(game, delay: float = 3.0, TD_variant = 'TDv1_4000'):
    # load correct achitecture for the model TODO make cleaner
    if TD_variant == 'TD0v1e_4000':
        model = TDGammonNetV1()
        model.load_state_dict(torch.load("/models/TD0v1e_4000.pt", map_location=torch.device('cpu')))
        model.eval()
    elif TD_variant == 'TD0v1e_10000':
        model = TDGammonNetV1()
        model.load_state_dict(torch.load("/models/TD0v1e_10000.pt", map_location=torch.device('cpu')))
        model.eval()
    elif TD_variant == 'TD0v1e_35000':
        model = TDGammonNetV1()
        model.load_state_dict(torch.load("/models/TD0v1e_35000.pt", map_location=torch.device('cpu')))
        model.eval()
    elif TD_variant == 'TD0v2e_4000':
        model = TDGammonNetV2()
        model.load_state_dict(torch.load("/models/TD0v2e_4000.pt", map_location=torch.device('cpu')))
        model.eval()
    elif TD_variant == 'TD0v2e_10000':
        model = TDGammonNetV2()
        model.load_state_dict(torch.load("/models/TD0v2e_10000.pt", map_location=torch.device('cpu')))
        model.eval()
    elif TD_variant == 'TD0v2e_35000':
        model = TDGammonNetV2()
        model.load_state_dict(torch.load("/models/TD0v2e_35000.pt", map_location=torch.device('cpu')))
        model.eval()
    elif TD_variant == 'MCV1e_4000':
        model = TDGammonNetV1()
        model.load_state_dict(torch.load("/models/MCV1e_4000.pt", map_location=torch.device('cpu')))
        model.eval()
    elif TD_variant == 'MCV1e_10000':
        model = TDGammonNetV1()
        model.load_state_dict(torch.load("/models/MCV1e_10000.pt", map_location=torch.device('cpu')))
        model.eval()
    elif TD_variant == 'MCV1e_35000':
        model = TDGammonNetV1()
        model.load_state_dict(torch.load("/models/MCV1e_35000.pt", map_location=torch.device('cpu')))
        model.eval()
    elif TD_variant == 'TDLv1e_4000':
        model = TDGammonNetV1()
        model.load_state_dict(torch.load("/models/TDLv1e_4000.pt", map_location=torch.device('cpu')))
        model.eval()
    elif TD_variant == 'TDLv1e_10000':
        model = TDGammonNetV1()
        model.load_state_dict(torch.load("/models/TDLv1e_10000.pt", map_location=torch.device('cpu')))
        model.eval()
    elif TD_variant == 'TDLv1e_35000':
        model = TDGammonNetV1()
        model.load_state_dict(torch.load("/models/TDLv1e_35000.pt", map_location=torch.device('cpu')))
        model.eval()
    
    else:
        raise ValueError(f"Unknown TD variant: {TD_variant}")


    if game.game_over:
        return game.get_board_state()

    moves = game.get_all_available_moves()
    if not moves:
        return game.get_board_state()

    best_score = -float('inf')
    best_move = None

    # evaluate each legal move by simulating on a copy
    for new_state, move in generate_pip_successors(game):        
        x = get_board_features(new_state)
        with torch.no_grad():
            y = model(x)
        # get the output based on what color the agent is playing at
        if game.current_player == 1: # if gammon win [1,0,0,0] or [0,1,0,0] for white
            score = y[0] + 2 * y[1]
        else:
            score = y[2] + 2 * y[3]
        if score > best_score:
            best_score, best_move = score, move

    time.sleep(delay)

    start, end = best_move
    game.make_move(start, end)
    print("TD ", TD_variant," move executed:", best_move)

    return game.get_board_state()
