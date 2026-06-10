import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt

class NeuralCA(nn.Module):
    def __init__(self, channels=16, hidden_size=128):
        super().__init__()
        self.channels = channels
        
        self.net = nn.Sequential(
            nn.Conv2d(channels * 3, hidden_size, 1),
            nn.ReLU(),
            nn.Conv2d(hidden_size, channels, 1)
        )

    def perceive(self, x):
        ident = torch.tensor([[0., 0., 0.], [0., 1., 0.], [0., 0., 0.]])
        sobel_x = torch.tensor([[-1., 0., 1.], [-2., 0., 2.], [-1., 0., 1.]]) / 8.0
        sobel_y = torch.tensor([[-1., -2., -1.], [0., 0., 0.], [1., 2., 1.]]) / 8.0
        
        filters = torch.stack([ident, sobel_x, sobel_y]).view(3, 1, 3, 3)
        filters = filters.repeat(self.channels, 1, 1, 1).to(x.device)
        
        return F.conv2d(x, filters, padding=1, groups=self.channels)

    def forward(self, x, update_rate=0.5):
        y = self.perceive(x)
        dx = self.net(y)
        
        update_mask = (torch.rand(x[:, :1, :, :].shape, device=x.device) < update_rate).float()
        alive_mask = F.max_pool2d(x[:, 3:4, :, :], kernel_size=3, stride=1, padding=1) > 0.1
        
        x = x + dx * update_mask
        x = x * alive_mask.float()
        
        return x

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CHANNELS = 16
GRID_SIZE = 40

model = NeuralCA(channels=CHANNELS).to(DEVICE)

def get_initial_seed(batch_size=1):
    seed = torch.zeros(batch_size, CHANNELS, GRID_SIZE, GRID_SIZE).to(DEVICE)
    seed[:, :, GRID_SIZE//2, GRID_SIZE//2] = 1.0 
    return seed

def apply_damage(x, radius=5):
    mask = torch.ones_like(x)
    center = GRID_SIZE // 2
    Y, X = torch.meshgrid(torch.arange(GRID_SIZE), torch.arange(GRID_SIZE), indexing='ij')
    dist = (X - center)**2 + (Y - center)**2
    mask[:, :, dist <= radius**2] = 0.0
    return x * mask

state = get_initial_seed()
growth_history = []

with torch.no_grad():
    for step in range(64):
        state = model(state)
        if step in [0, 16, 32, 63]:
            rgb = state[0, :3, :, :].permute(1, 2, 0).cpu().clamp(0, 1).numpy()
            growth_history.append((step, rgb))

damaged_state = apply_damage(state, radius=8)
recovery_history = [(0, damaged_state[0, :3, :, :].permute(1, 2, 0).cpu().clamp(0, 1).numpy())]

with torch.no_grad():
    for step in range(1, 65):
        damaged_state = model(damaged_state)
        if step in [16, 32, 64]:
            rgb = damaged_state[0, :3, :, :].permute(1, 2, 0).cpu().clamp(0, 1).numpy()
            recovery_history.append((step, rgb))

fig, axes = plt.subplots(1, 4, figsize=(16, 4))
fig.suptitle("Task 3: Growth Process", fontsize=16)

for i, (step, img) in enumerate(growth_history):
    axes[i].imshow(img)
    axes[i].set_title(f"Step {step}")
    axes[i].axis('off')

plt.tight_layout()
plt.show()

fig, axes = plt.subplots(1, 4, figsize=(16, 4))
fig.suptitle("Task 4: Damage and Recovery", fontsize=16)

for i, (step, img) in enumerate(recovery_history):
    axes[i].imshow(img)
    axes[i].set_title(f"Step {step}" if step > 0 else "Damaged State")
    axes[i].axis('off')

plt.tight_layout()
plt.show()