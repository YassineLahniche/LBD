import random

def get_best_actions(agent, states):
    """
    Get the best actions for multiple states using the trained Q-table,
    ensuring demand is always met while minimizing grid usage.
    
    Parameters:
    - agent: The QAgent instance
    - states: List of states to evaluate
    
    Returns:
    - Dictionary mapping each state to its best action tuple (pv, wt, grid)
    """
    best_actions = {}
    for state in states:
        state_key = agent.discretize_state(state)  # Convert to discrete form
        demand = state[2]  # Extract demand from state
        pv_power = state[0]  # Available PV power per unit
        wind_power = state[1]  # Available wind power per unit
        
        # Get best renewable action from Q-table if available
        if state_key in agent.q_table and agent.q_table[state_key]:
            best_idx = max(agent.q_table[state_key], key=agent.q_table[state_key].get)
            pv_count, wt_count, _ = agent.idx_to_action(best_idx)  # Ignore grid from Q-table
        else:
            # Fallback to a random action for renewables if state is not in Q-table
            pv_count = random.choice(agent.action_space_pv)
            wt_count = random.choice(agent.action_space_wt)
        
        # Calculate energy from renewables with the selected action
        pv_energy = pv_count * pv_power
        wt_energy = wt_count * wind_power
        renewable_energy = pv_energy + wt_energy
        
        # Calculate exact grid power needed to meet demand
        required_grid_power = max(0, demand - renewable_energy)
        
        # Find the grid action value that is closest to but not less than required
        grid_options = sorted(agent.action_space_grid)
        
        # Find the smallest grid value that meets the requirement
        selected_grid = None
        for grid_option in grid_options:
            if grid_option >= required_grid_power:
                selected_grid = grid_option
                break
                
        # If no grid option is large enough, take the maximum available
        if selected_grid is None:
            selected_grid = max(grid_options)
            
            # If even max grid plus renewables doesn't meet demand, 
            # try to increase renewable usage
            if renewable_energy + selected_grid < demand:
                # Sort renewable options by energy production (highest first)
                pv_options = sorted([(p, p * pv_power) for p in agent.action_space_pv], 
                                   key=lambda x: x[1], reverse=True)
                wt_options = sorted([(w, w * wind_power) for w in agent.action_space_wt], 
                                   key=lambda x: x[1], reverse=True)
                
                # Try different combinations to minimize excess while meeting demand
                best_excess = float('inf')
                best_combo = (pv_count, wt_count, selected_grid)
                
                for p, p_energy in pv_options:
                    for w, w_energy in wt_options:
                        combined_energy = p_energy + w_energy + selected_grid
                        if combined_energy >= demand:
                            excess = combined_energy - demand
                            if excess < best_excess:
                                best_excess = excess
                                best_combo = (p, w, selected_grid)
                
                pv_count, wt_count, selected_grid = best_combo
        
        # Create the final action with exact grid power needed
        best_actions[tuple(state)] = (pv_count, wt_count, selected_grid)
    
    return best_actions
