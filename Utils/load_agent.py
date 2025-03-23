def load_agent(filepath='saved_agent.pkl'):
    """
    Load a previously saved agent
    
    Args:
        filepath: Path to the saved agent file
        
    Returns:
        The loaded EnhancedQAgent instance
    """
    with open(filepath, 'rb') as f:
        agent = pickle.load(f)
    
    print(f"Agent loaded successfully from {filepath}")
    print(f"Q-table size: {len(agent.q_table)} states")
    
    return agent