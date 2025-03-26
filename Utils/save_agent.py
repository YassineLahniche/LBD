def save_agent(agent, filepath='saved_agent.pkl'):
    """
    Save the trained agent to a file using pickle
    
    Args:
        agent: The EnhancedQAgent instance to save
        filepath: Path where the agent will be saved
    """    
    with open(filepath, 'wb') as f:
        pickle.dump(agent, f)
    
    print(f"Agent saved successfully to {filepath}")
    print(f"Q-table size: {len(agent.q_table)} states")