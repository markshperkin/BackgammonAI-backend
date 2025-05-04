import torch
import torch.nn as nn
import torch.nn.functional as F

class TDGammonNetV1(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(28, 80)
        self.fc2 = nn.Linear(80, 4)

        for w in self.parameters():
            nn.init.uniform_(w, -0.05, 0.05)

    def forward(self, x):
        h = torch.sigmoid(self.fc1(x))
        y = torch.sigmoid(self.fc2(h))
        return y

class TDGammonNetV2(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(28, 60)
        self.fc15 = nn.Linear(60,30)
        self.fc2 = nn.Linear(30, 4)

        for w in self.parameters():
            nn.init.uniform_(w, -0.05, 0.05)

    def forward(self, x):
        h = torch.sigmoid(self.fc1(x))
        h2 = torch.sigmoid(self.fc15(h))
        y = torch.sigmoid(self.fc2(h2))
        return y

def td_update(model, traces, x_t, x_tp1, alpha=0.001, gamma=0.99, lambd=0.0):

    # forward pass
    y_t = model(x_t)
    if x_tp1.shape[-1] == 4:   
        y_tp1 = x_tp1
    else:
        y_tp1 = model(x_tp1)

    # compute TD error vector δ
    delta = (y_tp1 - y_t).detach()
    error = delta.norm().item()

    # compute gradient of Y(s_t)
    model.zero_grad()
    y_t.backward(-delta)  

    # update traces and weights
    with torch.no_grad():
        for p in model.parameters():
            grad = p.grad
            # update eligibility trace: decay + current gradient
            traces[p] = gamma * lambd * traces[p] + grad
            # apply weight update
            p += alpha * traces[p]
    return error