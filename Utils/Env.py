import numpy as np
import random
from collections import deque
import gym
from gym import spaces

class ReplayBuffer:
    """
    Experience replay buffer to store and sample transitions.
    """
    def __init__(self, capacity=100000):
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity
    
    def add(self, state, action, reward, next_state, done):
        """Add experience to buffer"""
        experience = (state, action, reward, next_state, done)
        self.buffer.append(experience)
    
    def sample(self, batch_size):
        """Randomly sample batch of experiences"""
        # Make sure we don't sample more than buffer size
        batch_size = min(batch_size, len(self.buffer))
        
        # Sample random indices
        indices = random.sample(range(len(self.buffer)), batch_size)
        
        # Get samples
        states, actions, rewards, next_states, dones = [], [], [], [], []
        for i in indices:
            s, a, r, s_, d = self.buffer[i]
            states.append(s)
            actions.append(a)
            rewards.append(r)
            next_states.append(s_)
            dones.append(d)
        
        return (
            np.array(states), 
            np.array(actions), 
            np.array(rewards).reshape(-1, 1), 
            np.array(next_states),
            np.array(dones).reshape(-1, 1)
        )
    
    def __len__(self):
        """Return current buffer size"""
        return len(self.buffer)
    
    def is_ready(self, batch_size):
        """Check if buffer has enough experiences"""
        return len(self) >= batch_size

class HybridEnergyEnv(gym.Env):
    def __init__(self):
        super(HybridEnergyEnv, self).__init__()

        # Define state and action sizes
        self.state_size = 4  # [P_solar, P_wind, Energy demand, Grid price]
        self.action_size = 3  # [N_pv, N_wt, P_grid]
        self.cost_weight = 0.6
        self.co2_weight = 0.4

        # Action space bounds
        self.action_low = np.array([0, 0, 0])  # Min panels, min turbines, min grid power
        self.action_high = np.array([300, 50, 200])  # Max panels, max turbines, max grid power

        # Define action and observation spaces
        self.action_space = spaces.Box(
            low=self.action_low,
            high=self.action_high,
            dtype=np.float32
        )

        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0]),  # Min values for state
            high=np.array([0.4, 20, 200, 0.1]),  # Max values for state
            dtype=np.float32
        )

        # Emission factors (gCO2/kWh)
        self.EF_PV = 50  # Emission factor per solar panel
        self.EF_WT = 10  # Emission factor per wind turbine
        self.EF_grid = 800  # Emission factor for grid power

        # Initialize state
        self.current_state = None
        self.reset()

    def reset(self):
        """Reset the environment to an initial state."""
        self.current_state = np.array([0, 0, 1000, 0.1])  # Example initial state
        return self.current_state

    def calculate_cost(self, action, state):
        """Calculate the comprehensive cost component of the reward.
        
        Args:
            action (array): Contains [N_pv, N_wt, P_grid] - number of PV panels, 
                            wind turbines, and grid power in kW
            state (array): Contains [P_solar, P_wind, Energy demand, Grid price]
        
        Returns:
            float: Negative cost (reward component)
        """
        # Extract values from action and state
        pv_count, wt_count, grid_power = action
        p_solar, p_wind, energy_demand, grid_price = state
        
        # Calculate actual power generation
        pv_power_per_panel = 0.4  # kW per panel
        wt_power_per_turbine = 20  # kW per turbine
        pv_power = pv_count * p_solar  # p_solar is capacity factor
        wt_power = wt_count * p_wind  # p_wind is capacity factor
        
        # Capital costs (one-time costs amortized over lifetime)
        pv_capex = 1000  # $ per kW
        wt_capex = 1500  # $ per kW
        pv_lifetime = 25 * 365 * 24  # hours (25 years)
        wt_lifetime = 20 * 365 * 24  # hours (20 years)
        
        # Amortized capital costs per hour
        pv_capital_cost = (pv_count * pv_power_per_panel * pv_capex) / pv_lifetime
        wt_capital_cost = (wt_count * wt_power_per_turbine * wt_capex) / wt_lifetime
        
        # Operation and maintenance costs
        pv_om_cost = pv_count * pv_power_per_panel * 0.015  # $0.015 per kW per hour
        wt_om_cost = wt_count * wt_power_per_turbine * 0.025  # $0.025 per kW per hour
        
        # Grid electricity costs (using grid_price from state)
        grid_cost = max(0, grid_power) * grid_price  # Only pay for imported power
        
        # Revenue from excess energy if renewable generation exceeds demand
        renewable_generation = pv_power + wt_power
        excess_energy = max(0, renewable_generation - energy_demand)
        
        # Land use costs
        pv_land_area = pv_count * 8  # 8 m² per panel
        wt_land_area = wt_count * 400  # 400 m² per wind turbine
        land_lease_cost = (pv_land_area + wt_land_area) * 0.0001  # $ per m² per hour
        
        # Total cost calculation
        total_cost = (
            pv_capital_cost + wt_capital_cost +
            pv_om_cost + wt_om_cost +
            grid_cost +
            land_lease_cost
        )
        
        return -total_cost  # Negative as we want to minimize cost
    
    def calculate_co2(self, action, state):
        """Calculate comprehensive CO2 emissions component of the reward.
        
        Args:
            action (array): Contains [N_pv, N_wt, P_grid] - number of PV panels, 
                            wind turbines, and grid power in kW
            state (array): Contains [P_solar, P_wind, Energy demand, Grid price]
        
        Returns:
            float: Negative CO2 emissions (reward component)
        """
        # Extract values from action and state
        pv_count, wt_count, grid_power = action
        p_solar, p_wind, energy_demand, grid_price = state
        
        # Calculate actual power generation
        pv_power_per_panel = 0.4  # kW per panel
        wt_power_per_turbine = 20  # kW per turbine
        pv_power = pv_count * pv_power_per_panel * p_solar  # p_solar is capacity factor
        wt_power = wt_count * wt_power_per_turbine * p_wind  # p_wind is capacity factor
        
        # Convert from gCO2/kWh to kgCO2/kWh for consistency
        ef_pv = self.EF_PV / 1000  # kg CO2/kWh
        ef_wt = self.EF_WT / 1000  # kg CO2/kWh
        ef_grid = self.EF_grid / 1000  # kg CO2/kWh
        
        # Lifecycle emissions from manufacturing and installation
        # Amortized over lifetime of equipment
        pv_lifetime = 25 * 365 * 24  # hours (25 years)
        wt_lifetime = 20 * 365 * 24  # hours (20 years)
        pv_lifecycle_co2 = 40  # kg CO2-eq per kW
        wt_lifecycle_co2 = 11  # kg CO2-eq per kW
        
        # Hourly lifecycle emissions
        pv_manufacturing_co2 = (pv_count * pv_power_per_panel * pv_lifecycle_co2) / pv_lifetime
        wt_manufacturing_co2 = (wt_count * wt_power_per_turbine * wt_lifecycle_co2) / wt_lifetime
        
        # Operational emissions
        pv_op_co2 = pv_power * ef_pv
        wt_op_co2 = wt_power * ef_wt
        grid_co2 = max(0, grid_power) * ef_grid
        
        # Maintenance emissions
        pv_maintenance_co2 = pv_count * 0.0002  # kg CO2 per panel per hour
        wt_maintenance_co2 = wt_count * 0.001  # kg CO2 per turbine per hour
        
        # Total emissions calculation
        total_co2 = (
            pv_manufacturing_co2 + wt_manufacturing_co2 +
            pv_op_co2 + wt_op_co2 +
            pv_maintenance_co2 + wt_maintenance_co2 +
            grid_co2 
        )
        
        return -total_co2  # Negative as we want to minimize emissions
    
    def calculate_reward(self, action, state):
        """Calculate the combined reward from cost and emissions components.
        
        Args:
            action (array): [N_pv, N_wt, P_grid]
            state (array): [P_solar, P_wind, Energy demand, Grid price]
            
        Returns:
            float: Combined reward value
        """
        # Calculate cost and emissions components
        cost_component = self.calculate_cost(action, state)
        co2_component = self.calculate_co2(action, state)
        

        
        # Calculate combined reward
        reward = (self.cost_weight * cost_component) + (self.co2_weight * co2_component)
        
        # Add penalty for not meeting energy demand
        p_solar, p_wind, energy_demand, grid_price = state
        pv_count, wt_count, grid_power = action
        pv_power_per_panel = 0.4  # kW per panel
        wt_power_per_turbine = 20  # kW per turbine
        
        total_generation = (pv_count * p_solar) + \
                           (wt_count * p_wind) + \
                           grid_power
        
        if total_generation < energy_demand:
            # Penalty for not meeting demand
            shortage = energy_demand - total_generation
            demand_penalty = -100 * shortage / energy_demand
            reward += demand_penalty
        
        return reward

    def step(self, action):
        """Execute one time step in the environment."""
        # Extract action components
        N_pv = int(action[0])  # Number of PV panels (integer)
        N_wt = int(action[1])  # Number of wind turbines (integer)
        P_grid_action = action[2]  # Grid power (continuous)
        
        # Extract current state
        P_solar, P_wind, energy_demand, grid_price = self.current_state
        
        # Compute energy generated
        pv_power_per_panel = 0.4  # kW per panel (previously 0.2 * 300W = 60W = 0.06kW)
        wt_power_per_turbine = 20  # kW per turbine (previously 0.5 * 10000W = 5000W = 5kW)
        
        P_pv = N_pv * P_solar   
        P_wt = N_wt * P_wind 
        total_renewable_energy = P_pv + P_wt
        
        # Compute energy deficit and grid usage
        energy_deficit = max(0, energy_demand - total_renewable_energy)
        grid_power_used = min(P_grid_action, energy_deficit)
        
        # Calculate cost and CO2 components using our comprehensive models
        cost_component = self.calculate_cost(action, self.current_state)
        co2_component = self.calculate_co2(action, self.current_state)
        

        # Compute reward using the weighted components
        reward = (self.cost_weight * cost_component) + (self.co2_weight * co2_component)
        
        # Add penalty for not meeting energy demand
        total_generation = total_renewable_energy + grid_power_used
        if total_generation < energy_demand:
            # Penalty for not meeting demand
            shortage = energy_demand - total_generation
            demand_penalty = -100 * shortage / energy_demand
            reward += demand_penalty
        
        # Update state with random fluctuations (keeping your original approach)
        next_P_solar = np.clip(P_solar + np.random.uniform(-50, 50), 0, 1200)
        next_P_wind = np.clip(P_wind + np.random.uniform(-2, 2), 0, 25)
        next_state = np.array([
            next_P_solar,
            next_P_wind,
            energy_demand,  # Demand remains fixed
            grid_price  # Grid price remains fixed
        ])
        
        self.current_state = next_state
        done = False
        
        # Provide additional info for debugging or monitoring
        info = {
            'renewable_energy': total_renewable_energy,
            'grid_energy': grid_power_used,
            'total_energy': total_generation,
            'energy_demand': energy_demand,
            'cost_component': -cost_component,  # Convert back to positive for reporting
            'co2_component': -co2_component,    # Convert back to positive for reporting
            'demand_met': total_generation >= energy_demand
        }
        
        return next_state, reward, done, info
