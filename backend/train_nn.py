import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np

log_dir = "game_logs"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ShaxDataset(Dataset):
    def __init__(self, log_dir):
        self.samples = []
        for filename in os.listdir(log_dir):
            if filename.endswith(".jsonl"):
                with open(os.path.join(log_dir, filename), "r") as f:
                    for line in f:
                        data = json.loads(line.strip())
                        if data["action"] is None:
                            continue
                        state = np.array(data["state"], dtype=np.float32)
                        action = data["action"]
                        if isinstance(action, int):
                            action_index = action
                        else:
                            # Convert (src, dest) -> flat 576 space (24x24)
                            action_index = action[0] * 24 + action[1]
                        reward = float(data["reward"]) / 10.0
                        self.samples.append((state, action_index, reward, data["phase"]))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        state, action, reward, phase = self.samples[idx]
        x = torch.tensor(state, dtype=torch.float32)
        y_policy = torch.tensor(action, dtype=torch.long)
        y_value = torch.tensor(reward, dtype=torch.float32)
        return x, y_policy, y_value, phase


class ShaxNet(nn.Module):
    def __init__(self, output_size):
        super().__init__()
        self.fc1 = nn.Linear(24, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 128)
        self.fc_policy = nn.Linear(128, output_size)
        self.fc_value = nn.Linear(128, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        policy_logits = self.fc_policy(x)
        value = torch.tanh(self.fc_value(x))
        return policy_logits, value

def train_model(epochs=10, batch_size=64, lr=1e-4, resume = True):
    print(f"Loading dataset... {log_dir}")
    dataset = ShaxDataset(log_dir)
    
    phase_counts = {"placement": 0, "removal": 0, "movement": 0}
    for _, _, _, phase in dataset:
        if phase in phase_counts:
            phase_counts[phase] += 1
    print("Samples per phase:", phase_counts)


    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model_placement = ShaxNet(output_size=24).to(DEVICE)
    model_removal = ShaxNet(output_size=24).to(DEVICE)
    model_movement = ShaxNet(output_size=24 * 24).to(DEVICE)

    if resume:
        try:
            model_placement.load_state_dict(torch.load("placement_model.pth", map_location=DEVICE))
            model_removal.load_state_dict(torch.load("removal_model.pth", map_location=DEVICE))
            model_movement.load_state_dict(torch.load("movement_model.pth", map_location=DEVICE))
            print("✅ Resumed from existing models.")
        except FileNotFoundError:
            print("⚠️ Model files not found. Starting from scratch.")

    optimizer_placement = optim.Adam(model_placement.parameters(), lr=lr)
    optimizer_removal = optim.Adam(model_removal.parameters(), lr=lr)
    optimizer_movement = optim.Adam(model_movement.parameters(), lr=lr)

    loss_policy_fn = nn.CrossEntropyLoss()
    loss_value_fn = nn.MSELoss()

    for epoch in range(epochs):
        total_policy_loss = 0
        total_value_loss = 0
        model_placement.train()
        model_removal.train()
        model_movement.train()

        for batch in dataloader:
            states, actions, rewards, phases = batch
            states = states.to(DEVICE)
            actions = actions.to(DEVICE)
            rewards = rewards.to(DEVICE).view(-1, 1)

            for phase in ["placement","removal", "movement"]:
                phase_mask = [i for i, p in enumerate(phases) if p == phase]
                if not phase_mask:
                    continue

                phase_states = states[phase_mask]
                phase_actions = actions[phase_mask]
                phase_rewards = rewards[phase_mask]

                if phase == "placement":
                    logits, values = model_placement(phase_states)
                    optimizer = optimizer_placement
                elif phase == "removal":
                    logits, values = model_removal(phase_states)
                    optimizer = optimizer_removal
                else:
                    logits, values = model_movement(phase_states)
                    optimizer = optimizer_movement

                loss_policy = loss_policy_fn(logits, phase_actions)
                loss_value = loss_value_fn(values, phase_rewards)
                loss = loss_policy + loss_value

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                total_policy_loss += loss_policy.item()
                total_value_loss += loss_value.item()

        print(f"Epoch {epoch+1}/{epochs} | Policy Loss: {total_policy_loss:.4f} | Value Loss: {total_value_loss:.4f}")

    # Save models
    torch.save(model_placement.state_dict(), "placement_model.pth")
    torch.save(model_movement.state_dict(), "movement_model.pth")
    torch.save(model_removal.state_dict(), "removal_model.pth")
    print("Models saved.")


if __name__ == "__main__":
    train_model(epochs=500)
