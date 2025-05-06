import random
from matplotlib import pyplot as plt
import torch
from TDGammonNet import TDGammonNetV1, mc_update
from game import Backgammon
from gameForAI import get_board_features, generate_pip_successors

def train_mc(num_episodes: int = 10000):
    device = torch.device("cpu")
    print(device)
    modelName = "MCv1eW_10000.pt"
    print("MC Training started", modelName, num_episodes)
    model = TDGammonNetV1().to(device)
    losses = []
    avg = []
    alpha = 0.001
    epsilon = 0.1

    for ep in range(1, num_episodes):
        # decay learning rate at milestones
        if ep == 4000:
            # alpha *= 0.1
            epsilon = 0.01

        game = Backgammon()
        game.roll_dice()

        episode = []  # to collect (state, reward_vec) pairs

        # play one full game episode
        while not game.check_game_over():
            x_t = get_board_features(game).to(device)
            best_score = -float("inf")
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
                episode.append((x_t, torch.zeros(4, device=device)))
                continue

            start, end = best_move
            game.make_move(start, end)

            x_tp1 = get_board_features(game).to(device)
            episode.append((x_t, torch.zeros(4, device=device)))

        # episode terminal: assign terminal reward vector
        winner = game.check_game_over()
        if winner == 1:
            # White won
            if game.borne_off_black == 0:
                terminal_reward = torch.tensor([0, 1, 0, 0], dtype=torch.float32, device=device)
            else:
                terminal_reward = torch.tensor([1, 0, 0, 0], dtype=torch.float32, device=device)
        else:
            # Black won
            if game.borne_off_white == 0:
                terminal_reward = torch.tensor([0, 0, 0, 1], dtype=torch.float32, device=device)
            else:
                terminal_reward = torch.tensor([0, 0, 1, 0], dtype=torch.float32, device=device)

        x_T = get_board_features(game).to(device)
        episode.append((x_T, terminal_reward))

        loss = mc_update(model, episode, alpha=alpha)
        losses.append(loss)

        if ep % 100 == 0:
            avg_loss = sum(losses[-100:]) / 100
            avg.append(avg_loss)
            print(f"Episode {ep}; Avg Loss: {avg_loss:.6f}")

    torch.save(model.state_dict(), modelName)
    print("MC Training Complete")

    plt.plot(avg)
    plt.xlabel("100-episode blocks")
    plt.ylabel("Avg MC Loss")
    plt.title("Monte Carlo Training Loss")
    plt.show()

if __name__ == "__main__":
    train_mc()
