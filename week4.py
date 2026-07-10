import gymnasium as gym
from gymnasium import spaces
import numpy as np
import torch
import torch.nn as nn

# PART 1: Analyze Existing Systems


# PART 2: Design a Learnable World
class ZombieEvacuationEnv(gym.Env):
    
    def __init__(self):
        super().__init__()
        # Observation: [dx_zombie, dy_zombie, dx_exit, dy_exit]
        self.observation_space = spaces.Box(low=-10.0, high=10.0, shape=(4,), dtype=np.float32)
        
        # Action: [move_x, move_y]
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)
        
        self.world_size = 10.0
        self.exit_pos = np.array([9.0, 9.0], dtype=np.float32)
        self.max_steps = 30
        self.current_step = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.agent_pos = np.array([1.0, 1.0], dtype=np.float32)
        self.zombie_pos = np.array([5.0, 5.0], dtype=np.float32)
        return self._get_obs(), {}

    def _get_obs(self):
        delta_zombie = self.zombie_pos - self.agent_pos
        delta_exit = self.exit_pos - self.agent_pos
        return np.concatenate([delta_zombie, delta_exit]).astype(np.float32)

    def step(self, action):
        self.current_step += 1
        
        # 1. Apply Agent Action (The Learned Behavior)
        self.agent_pos += action * 0.5
        self.agent_pos = np.clip(self.agent_pos, 0.0, self.world_size)
        
        # 2. Apply Zombie Movement (The Fixed/Hardcoded Behavior)
        zombie_vec = self.agent_pos - self.zombie_pos
        dist_to_agent = np.linalg.norm(zombie_vec)
        if dist_to_agent > 0:
            self.zombie_pos += (zombie_vec / dist_to_agent) * 0.2 
            
        # 3. Define Success (Reward)
        dist_to_exit = np.linalg.norm(self.exit_pos - self.agent_pos)
        reward, terminated = -0.1, False # Step penalty
        
        if dist_to_exit < 1.0:
            reward, terminated = 10.0, True
            print("   -> SUCCESS: Reached the exit!")
        elif dist_to_agent < 0.5:
            reward, terminated = -10.0, True
            print("   -> FAILED: Caught by zombie!")
            
        truncated = self.current_step >= self.max_steps
        if truncated and not terminated:
            print("   -> TIMEOUT: Ran out of time.")
            
        return self._get_obs(), reward, terminated, truncated, {}

# PART 3: Replace a Rule with Learning
class AgentBrain(nn.Module):
   
    def __init__(self, input_size=4, output_size=2):
        super(AgentBrain, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 16),
            nn.ReLU(),
            nn.Linear(16, output_size),
            nn.Tanh() # Outputs between -1 and +1 for movement
        )

    def forward(self, local_observation):
        return self.network(local_observation)

# PART 4: Predict Emergent Behavior
# MAIN EXECUTION
def main():
   
    print("PARTS 2 & 3: RUNNING THE UNTRAINED LEARNABLE WORLD")
    env = ZombieEvacuationEnv()
    brain = AgentBrain() # Random weights (untrained)
    
    # Run a short simulation
    obs, _ = env.reset()
    done = False
    
    while not done:
        obs_tensor = torch.tensor(obs, dtype=torch.float32)
        with torch.no_grad():
            action = brain(obs_tensor).numpy()
            
        obs, reward, terminated, truncated, _ = env.step(action)
        
        print(f"Step {env.current_step:02d} | "
              f"Pos: ({env.agent_pos[0]:.1f}, {env.agent_pos[1]:.1f}) | "
              f"Action: [{action[0]:.2f}, {action[1]:.2f}] | "
              f"Reward: {reward:.1f}")
        
        done = terminated or truncated

    
if __name__ == "__main__":
    main()