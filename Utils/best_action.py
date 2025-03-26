def get_best_actions(agent, states):
    """
    Get the best actions for multiple states using the trained Q-table,
    ensuring demand is always met while minimizing grid usage when possible.

    Parameters:
    - agent: The QAgent instance
    - states: List of states to evaluate

    Returns:
    - Dictionary mapping each state to its best action tuple (pv, wt, grid)
    """
    best_actions = {}

    for state in states:
        state_key = agent.discretize_state(state)  # Convert to discrete form

        # Extract demand from state (assuming demand is the 3rd element)
        demand = state[2]

        if state_key in agent.q_table and agent.q_table[state_key]:
            # Find the index of the best action from Q-table
            best_idx = max(agent.q_table[state_key], key=agent.q_table[state_key].get)
            # Convert index back to action tuple
            best_action = agent.idx_to_action(best_idx)
        else:
            # Fallback to a random action if state is not in Q-table
            pv = random.choice(agent.action_space_pv)
            wt = random.choice(agent.action_space_wt)
            grid = random.choice(agent.action_space_grid)
            best_action = (pv, wt, grid)

        # Calculate energy from renewables with the selected action
        pv_count, wt_count, _ = best_action
        pv_power = state[0]  # Default if not in state
        wind_power = state[1]        # Default if not in state


        pv_energy = pv_count *  pv_power
        wt_energy = wt_count * wind_power
        renewable_energy = pv_energy + wt_energy

        # Determine required grid power to meet demand
        required_grid_power = max(0, demand - renewable_energy)

        # Find closest grid power value in discretized space that meets or exceeds requirement
        grid_options = [g for g in agent.action_space_grid if g >= required_grid_power]
        if grid_options:
            # Choose the smallest grid power that meets demand
            new_grid_power = min(grid_options)
        else:
            # If no grid option is large enough, take the maximum available
            new_grid_power = max(agent.action_space_grid)

        # Create the adjusted action
        adjusted_action = (pv_count, wt_count, new_grid_power)

        # Check if this meets demand
        total_energy = renewable_energy + new_grid_power
        if total_energy < demand:
            # This scenario should be rare given our grid power selection
            # But if it happens, we need to adjust renewables upward

            # Try different combinations of PV and WT
            best_solution = None
            min_excess = float('inf')

            for p in sorted(agent.action_space_pv, reverse=True):
                for w in sorted(agent.action_space_wt, reverse=True):
                    p_energy = p * pv_power
                    w_energy = w * wind_power
                    r_energy = p_energy + w_energy

                    # Calculate remaining demand
                    remaining = max(0, demand - r_energy)

                    # Find grid power that meets or exceeds remaining demand
                    grid_options = [g for g in agent.action_space_grid if g >= remaining]
                    if grid_options:
                        g = min(grid_options)
                        test_total = r_energy + g
                        excess = test_total - demand

                        # Keep track of solution with minimum excess
                        if excess < min_excess:
                            min_excess = excess
                            best_solution = (p, w, g)

            if best_solution:
                adjusted_action = best_solution

        best_actions[tuple(state)] = adjusted_action

    return best_actions