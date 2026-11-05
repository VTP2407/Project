import random
import numpy as np
from typing import Dict, Any, List

class DiabetesHealthEnv:
    """
    Simulated patient health-support environment for educational reinforcement learning.
    State representation: (Glucose_Category, Activity_Category, Nutrition_Category)
    - Glucose: 0 (Low <70), 1 (Normal 70-139), 2 (Elevated 140-199), 3 (High >=200)
    - Activity: 0 (Sedentary), 1 (Moderate), 2 (Active)
    - Nutrition: 0 (Unhealthy), 1 (Average), 2 (Healthy)
    Total discrete states: 4 * 3 * 3 = 36 states.
    """
    
    ACTION_NAMES = [
        "Khuyến nghị Giáo dục Vận động Thể chất",
        "Khuyến nghị Dinh dưỡng & Kiểm soát Carb",
        "Khướng dẫn Tự theo dõi Đường huyết thường xuyên",
        "Khuyến nghị Thăm khám Bác sĩ Chuyên khoa"
    ]
    
    def __init__(self):
        self.num_glucose = 4
        self.num_activity = 3
        self.num_nutrition = 3
        self.num_states = self.num_glucose * self.num_activity * self.num_nutrition
        self.num_actions = len(self.ACTION_NAMES)
        self.reset()
        
    def encode_state(self, g: int, a: int, n: int) -> int:
        return g * 9 + a * 3 + n
        
    def decode_state(self, state_id: int):
        g = state_id // 9
        rem = state_id % 9
        a = rem // 3
        n = rem % 3
        return g, a, n
        
    def reset(self) -> int:
        self.g = random.randint(0, 3)
        self.a = random.randint(0, 2)
        self.n = random.randint(0, 2)
        self.current_state = self.encode_state(self.g, self.a, self.n)
        self.steps = 0
        return self.current_state
        
    def step(self, action: int):
        self.steps += 1
        reward = 0.0
        g, a, n = self.decode_state(self.current_state)
        
        # Educational Action Logic
        if action == 0:  # Physical Activity Education
            if a < 2:
                a += 1
                reward += 3.0
            if g in [2, 3]:  # Helps lower glucose
                g = max(1, g - 1)
                reward += 5.0
            elif g == 0:  # Exercising during hypoglycemia is dangerous
                reward -= 10.0
                
        elif action == 1:  # Nutrition Education
            if n < 2:
                n += 1
                reward += 3.0
            if g in [2, 3]:
                g = max(1, g - 1)
                reward += 4.0
            elif g == 0:
                g = 1  # Glucose stabilization
                reward += 6.0
                
        elif action == 2:  # Self-monitoring
            reward += 2.0
            if g == 1:
                reward += 2.0
                
        elif action == 3:  # Physician consultation
            if g in [0, 3]:  # Crucial for severe conditions
                reward += 10.0
                g = 1  # Clinical intervention brings back to control
            else:
                reward -= 1.0  # Over-consulting for mild stable states
                
        # Bonus for maintaining optimal state
        if g == 1 and a >= 1 and n >= 1:
            reward += 5.0
            
        # Add slight stochastic lifestyle drift
        if random.random() < 0.15:
            g = min(3, max(0, g + random.choice([-1, 1])))
            
        self.current_state = self.encode_state(g, a, n)
        done = (self.steps >= 20)  # 20 simulated interaction steps per episode
        
        return self.current_state, reward, done

class QLearningAgent:
    def __init__(self, num_states: int = 36, num_actions: int = 4, alpha: float = 0.1, gamma: float = 0.95, epsilon: float = 0.1):
        self.num_states = num_states
        self.num_actions = num_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.Q = np.zeros((num_states, num_actions))
        
    def select_action(self, state: int) -> int:
        if random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        return int(np.argmax(self.Q[state]))
        
    def update(self, state: int, action: int, reward: float, next_state: int):
        best_next = np.max(self.Q[next_state])
        td_target = reward + self.gamma * best_next
        td_error = td_target - self.Q[state, action]
        self.Q[state, action] += self.alpha * td_error

def run_simulation(episodes: int = 500, alpha: float = 0.1, gamma: float = 0.95, epsilon: float = 0.1) -> Dict[str, Any]:
    env = DiabetesHealthEnv()
    agent = QLearningAgent(num_states=env.num_states, num_actions=env.num_actions, alpha=alpha, gamma=gamma, epsilon=epsilon)
    
    episode_rewards = []
    moving_avg_rewards = []
    
    for ep in range(episodes):
        state = env.reset()
        total_reward = 0.0
        done = False
        while not done:
            action = agent.select_action(state)
            next_state, reward, done = env.step(action)
            agent.update(state, action, reward, next_state)
            state = next_state
            total_reward += reward
            
        episode_rewards.append(round(total_reward, 2))
        window = episode_rewards[-min(len(episode_rewards), 20):]
        moving_avg_rewards.append(round(sum(window) / len(window), 2))
        
    # Summarize best policy for sample states
    glucose_labels = ["Hạ đường huyết (<70)", "Bình thường (70-139)", "Đường huyết cao (140-199)", "Rất cao (>=200)"]
    policy_summary = []
    for g_idx, g_lbl in enumerate(glucose_labels):
        st = env.encode_state(g_idx, 0, 0) # Sedentary, Unhealthy nutrition
        best_a = int(np.argmax(agent.Q[st]))
        policy_summary.append({
            "glucose_state": g_lbl,
            "recommended_action": env.ACTION_NAMES[best_a],
            "q_values": [round(float(v), 2) for v in agent.Q[st]]
        })
        
    return {
        "episodes": episodes,
        "alpha": alpha,
        "gamma": gamma,
        "epsilon": epsilon,
        "final_average_reward": moving_avg_rewards[-1],
        "reward_history": episode_rewards[::max(1, episodes // 50)], # Sample ~50 points for chart
        "moving_average": moving_avg_rewards[::max(1, episodes // 50)],
        "policy_summary": policy_summary,
        "action_names": env.ACTION_NAMES
    }
