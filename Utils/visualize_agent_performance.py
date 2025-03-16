def visualize_agent_performance(agent, env, rewards_history, episodes=5, max_steps=20, sample_size=100):
    """
    Optimized visualization suite for evaluating the Q-learning agent.
    Reduces computational load by creating fewer plots and sampling data.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    from matplotlib.colors import LinearSegmentedColormap
    
    # Set plot style once
    plt.style.use('ggplot')
    
    # Function to collect testing data - moved outside main flow to avoid repetition
    def collect_test_data(num_episodes=episodes, max_steps=max_steps):
        pv_values, wt_values, grid_values = [], [], []
        energy_totals, state_list = [], []
        
        for episode in range(num_episodes):
            state = env.reset()
            
            for step in range(max_steps):
                action = agent.choose_action(state)
                pv_values.append(action[0])
                wt_values.append(action[1])
                grid_values.append(action[2])
                
                # Calculate energy directly to avoid redundant calculations
                solar_factor = max(0.1, state[0] if len(state) > 0 else 0.5)
                wind_factor = max(0.1, state[1] if len(state) > 1 else 0.5)
                pv_energy = action[0] * 3 * solar_factor
                wt_energy = action[1] * 10 * wind_factor
                grid_energy = action[2]
                total_energy = pv_energy + wt_energy + grid_energy
                
                energy_totals.append(total_energy)
                state_list.append(state)
                
                next_state, reward, done, _ = env.step(action)
                state = next_state
                
                if done:
                    break
        
        return {
            'pv': pv_values, 
            'wt': wt_values, 
            'grid': grid_values,
            'energy': energy_totals,
            'states': state_list,
            'pv_energy': [pv * 3 for pv in pv_values],  # Pre-calculate for efficiency
            'wt_energy': [wt * 10 for wt in wt_values]
        }
    
    # ------- ESSENTIAL VISUALIZATIONS (ONLY THE MOST IMPORTANT) -------
    
    # Create a single 2x2 figure for the most important visualizations
    plt.figure(figsize=(12, 10))
    
    # 1. Training Rewards Over Time (Most important)
    plt.subplot(2, 2, 1)
    
    # Sample rewards history if it's large
    if len(rewards_history) > sample_size:
        sample_indices = np.linspace(0, len(rewards_history)-1, sample_size, dtype=int)
        sampled_rewards = [rewards_history[i] for i in sample_indices]
        x_values = sample_indices
    else:
        sampled_rewards = rewards_history
        x_values = range(len(rewards_history))
    
    plt.plot(x_values, sampled_rewards, color='blue', linewidth=2)
    plt.axhline(y=np.mean(rewards_history), color='red', linestyle='--', 
                label=f'Avg: {np.mean(rewards_history):.2f}')
    
    # Add rolling average only if we have enough data
    if len(rewards_history) >= 5:
        window_size = min(len(rewards_history) // 5, 10)
        if window_size > 1:
            rolling_mean = pd.Series(rewards_history).rolling(window=window_size).mean()
            # Sample the rolling mean the same way
            if len(rolling_mean) > sample_size:
                rolling_mean = [rolling_mean[i] for i in sample_indices]
            plt.plot(x_values, rolling_mean[:len(x_values)], color='green', linewidth=2, 
                     label=f'{window_size}-Ep Rolling Avg')
    
    plt.title('Training Rewards Progress')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.legend()
    
    # Collect test data once (not for every plot)
    test_data = collect_test_data()
    
    # 2. Energy Mix Pie Chart (Simple but informative)
    plt.subplot(2, 2, 2)
    
    # Calculate average contribution of each energy source
    avg_pv_energy = np.mean(test_data['pv_energy'])
    avg_wt_energy = np.mean(test_data['wt_energy'])
    avg_grid_energy = np.mean(test_data['grid'])
    total_avg = avg_pv_energy + avg_wt_energy + avg_grid_energy
    
    # Create energy mix pie chart
    energy_sources = ['PV Panels', 'Wind Turbines', 'Grid']
    energy_values = [avg_pv_energy, avg_wt_energy, avg_grid_energy]
    
    plt.pie(energy_values, labels=energy_sources, autopct='%1.1f%%', 
            startangle=90, shadow=True, explode=(0.05, 0.05, 0.05),
            colors=['gold', 'skyblue', 'lightgreen'])
    plt.title(f'Average Energy Source Mix\nTotal: {total_avg:.1f} units')
    
