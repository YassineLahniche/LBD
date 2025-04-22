import numpy as np

def naive_strategy(env, episodes=200, max_steps=5000, max_energy=200):
    """Industry standard heuristic-based strategy for energy management.
    Uses rule-based decision making with some adaptability."""
    total_rewards = []
    cost_values = []
    co2_values = []
    violations = 0
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        episode_violations = 0
        episode_cost = 0
        episode_co2 = 0
        
        for step in range(max_steps):
            # Get current state values
            pv_factor = state[0]  # Solar power factor
            wind_factor = state[1]  # Wind power factor
            
            # Rule-based decision making based on renewable conditions
            # If good renewable conditions, use more renewable sources
            if pv_factor > 0.6:  # Good solar conditions
                pv_panels = 200  # High solar utilization
            elif pv_factor > 0.3:  # Medium solar conditions
                pv_panels = 150  # Medium solar utilization
            else:  # Poor solar conditions
                pv_panels = 50   # Minimal solar utilization
            
            if wind_factor > 0.7:  # Good wind conditions
                wind_turbines = 35  # High wind utilization
            elif wind_factor > 0.4:  # Medium wind conditions
                wind_turbines = 20  # Medium wind utilization
            else:  # Poor wind conditions
                wind_turbines = 5   # Minimal wind utilization
            
            # Calculate expected renewable energy
            renewable_energy = (pv_panels * pv_factor) + (wind_turbines * wind_factor)
            
            # Determine grid power needed to meet demand
            # Industry typically aims for ~10% buffer over estimated need
            grid_power = max(0, min(1000, (max_energy - renewable_energy) * 1.1))
            
            # Round to nearest grid power increment
            grid_power = round(grid_power / 50) * 50
            
            # Final action
            action = (pv_panels, wind_turbines, grid_power)
            
            # Check for energy constraint violation
            total_energy = pv_panels * pv_factor + wind_turbines * wind_factor + grid_power
            if total_energy > max_energy:
                # Adjust grid power down
                excess = total_energy - max_energy
                adjusted_grid = max(0, grid_power - excess)
                # Round to nearest increment
                adjusted_grid = round(adjusted_grid / 50) * 50
                action = (pv_panels, wind_turbines, adjusted_grid)
                episode_violations += 1
            
            # Calculate metrics
            cost = env.calculate_cost(action, state)
            co2 = env.calculate_co2(action, state)
            
            # Combined reward
            reward = env.cost_weight * cost + env.co2_weight * co2
            
            state, env_reward, done, _ = env.step(action)
            
            total_reward += reward
            episode_cost += cost
            episode_co2 += co2
            
            if done:
                break
        
        violations += episode_violations
        total_rewards.append(total_reward)
        cost_values.append(episode_cost)
        co2_values.append(episode_co2)
    
    avg_reward = np.mean(total_rewards)
    avg_cost = np.mean(cost_values)
    avg_co2 = np.mean(co2_values)
    
    print(f"Industry standard strategy. Average reward: {avg_reward:.2f}")
    print(f"Average cost: {avg_cost:.2f}, Average CO2: {avg_co2:.2f}")
    print(f"Total violations: {violations}")
    
    return avg_reward, avg_cost, avg_co2, violations