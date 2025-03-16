def test_agent(agent, episodes=200, max_steps=10000):
    """Test the trained agent with energy constraint monitoring."""
    # Save exploration rate and set to minimum for testing
    original_epsilon = agent.epsilon
    agent.epsilon = agent.min_epsilon
    
    total_rewards = []
    violations = 0
    
    for episode in range(episodes):
        state = agent.env.reset()
        total_reward = 0
        episode_violations = 0
        
        for step in range(max_steps):
            action = agent.choose_action(state)
            
            # Check for energy violations
            total_energy = agent.estimate_total_energy(action, state)
            if total_energy > agent.max_energy:
                episode_violations += 1
            
            state, reward, done, _ = agent.env.step(action)
            total_reward += reward
            
            if done:
                break
        
        violations += episode_violations
        total_rewards.append(total_reward)
        
        if episode % 5 == 0:
            print(f"Test episode {episode}: Reward={total_reward:.2f}, Violations={episode_violations}")
    
    # Restore original exploration rate
    agent.epsilon = original_epsilon
    print(f"Testing complete. Average reward: {np.mean(total_rewards):.2f}, Total violations: {violations}")
    return np.mean(total_rewards)