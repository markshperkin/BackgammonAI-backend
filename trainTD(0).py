import random
from matplotlib import pyplot as plt
import torch
from TDGammonNet import TDGammonNetV1, TDGammonNetV2, td_update
from game import Backgammon
from gameForAI import get_board_features, generate_pip_successors

def train_td0(num_episodes: int = 1500000):
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = torch.device("cpu")
    print(device)
    modelName = "TDLv1e_1500000.pt"
    print("Training started for: ", modelName, num_episodes)
    model = TDGammonNetV1().to(device)
    traces = { p: torch.zeros_like(p, device=device) for p in model.parameters() }
    losses = []
    avg = []
    alpha = 0.001
    epsilon = 0.1
    for ep in range(1, num_episodes):
        for t in traces.values():
            t.zero_()
        if ep == 4000:
            # alpha *= 0.1
            epsilon = 0.01
        game = Backgammon()
        game.roll_dice()

        while not game.check_game_over():
            x_t = get_board_features(game).to(device)
            best_score = -float('inf')
            best_move = None
            moves = game.get_all_available_moves()
            if random.random() < epsilon and moves:
                start, end, _, _ = random.choice(moves)
                best_move = (start, end)
            else:
                for new_state, move in generate_pip_successors(game):
                    x_tp1 = get_board_features(new_state).to(device)
                    with torch.no_grad():
                        y = model(x_tp1)
                    if game.current_player == 1:
                        score = y[0] + 2 * y[1]
                    elif game.current_player == -1:
                        score = y[2] + 2 * y[3]
                    if score > best_score:
                        best_score = score
                        best_move = move
            if best_move is None:
                temp = game.get_board_state()
                x_tp1 = get_board_features(game).to(device)
                loss = td_update(model, traces, x_t, x_tp1, alpha=alpha, lambd=0.8)
                losses.append(loss)
                continue

            start, end = best_move
            game.make_move(start, end)

            x_tp1 = get_board_features(game).to(device)
            loss = td_update(model, traces, x_t, x_tp1, alpha=alpha, lambd=0.8)
            losses.append(loss)

        winner = game.check_game_over()

        if winner == 1:
            if game.borne_off_black == 0: 
                z = torch.tensor([0, 1, 0, 0], dtype=torch.float32).to(device)
            else:
                z = torch.tensor([1, 0, 0, 0], dtype=torch.float32).to(device)
        else:
            if game.borne_off_white == 0:
                z = torch.tensor([0, 0, 0, 1], dtype=torch.float32).to(device)
            else:
                z = torch.tensor([0, 0, 1, 0], dtype=torch.float32).to(device)

        x_T = get_board_features(game).to(device)
        loss = td_update(model, traces, x_T, z, alpha=alpha, gamma=1.0, lambd=0.8)
        losses.append(loss)
        if ep % 100 == 0:
            avg_loss = sum(losses[-100:]) / 100
            avg.append(avg_loss)
            print("finishing episode: ", ep, "; loss: ", avg_loss)


    torch.save(model.state_dict(), modelName)
    print("Training Complete")
    
    plt.plot(avg)
    plt.xlabel("episode")
    plt.ylabel("loss norm")
    plt.show()

if __name__ == "__main__":
    train_td0()