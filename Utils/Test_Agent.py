def test_agent(agent, episodes=100, max_steps=5000):
    """Test the trained agent with separate tracking of cost and CO2 metrics."""
    # Save exploration rate and set to minimum for testing
    original_epsilon = agent.epsilon
    agent.epsilon = agent.min_epsilon
    
    total_rewards = []
    cost_values = []
    co2_values = []
    violations = 0
    
    for episode in range(episodes):
        state = agent.env.reset()
        total_reward = 0
        episode_violations = 0
        episode_cost = 0
        episode_co2 = 0
        
        for step in range(max_steps):
            action = agent.choose_action(state)
            
            # Check for energy violations
            total_energy = agent.estimate_total_energy(action, state)
            if total_energy > agent.max_energy:
                episode_violations += 1
            
            # Calculate individual metrics
            cost = agent.env.calculate_cost(action, state)
            co2 = agent.env.calculate_co2(action, state)
            
            state, env_reward, done, _ = agent.env.step(action)
            
            # Use our calculated reward
            reward = env.cost_weight * cost + env.co2_weight * co2
            
            total_reward += reward
            episode_cost += cost
            episode_co2 += co2
            
            if done:
                break
        
        violations += episode_violations
        total_rewards.append(total_reward)
        cost_values.append(episode_cost)
        co2_values.append(episode_co2)
        
        if episode % 5 == 0:
            print(f"Test episode {episode}: Reward={total_reward:.2f}, Cost={episode_cost:.2f}, CO2={episode_co2:.2f}, Violations={episode_violations}")
    
    # Restore original exploration rate
    agent.epsilon = original_epsilon
    
    print(f"Testing complete. Average reward: {np.mean(total_rewards):.2f}")
    print(f"Average cost: {np.mean(cost_values):.2f}, Average CO2: {np.mean(co2_values):.2f}")
    print(f"Total violations: {violations}")
    
    return np.mean(total_rewards), np.mean(cost_values), np.mean(co2_values), violations