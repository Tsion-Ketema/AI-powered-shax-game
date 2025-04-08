from collections import Counter

from backend.train_nn import ShaxDataset
dataset = ShaxDataset("game_logs")
print(Counter([p for _,_,_,p in dataset]))

for i in range(5):
    _, _, reward, _ = dataset[i]
    print(reward)
import torch
print(torch.__version__)
print(torch.backends.mps.is_available())
