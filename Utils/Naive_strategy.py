def naive_strategy(env, episodes=100, max_steps=10000, max_energy=1000):
    """Simplified baseline strategy with energy constraint."""
    total_rewards = []
    violations = 0
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        episode_violations = 0
        
        for step in range(max_steps):
            # Start with naive action
            action = (50, 20, 500)
            
            # Check & adjust for energy constraint (simplified calculation)
            P_pv = state[0]
            P_wt = state[1]
            pv_energy = action[0]  * P_pv
            wt_energy = action[1] *  P_wt
            total_energy = pv_energy + wt_energy + action[2]
            
            if total_energy > max_energy:
                # Adjust grid power down
                excess = total_energy - max_energy
                adjusted_grid = max(0, action[2] - excess)
                action = (action[0], action[1], adjusted_grid)
                episode_violations += 1
            
            state, reward, done, _ = env.step(action)
            total_reward += reward
            
            if done:
                break
                
        violations += episode_violations
        total_rewards.append(total_reward)
    
    print(f"Naive strategy. Average reward: {np.mean(total_rewards):.2f}, Total violations: {violations}")
    return np.mean(total_rewards)