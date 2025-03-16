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

        # Action space bounds
        self.action_low = np.array([0, 0, 0])  # Min panels, min turbines, min grid power
        self.action_high = np.array([300, 50, 1000])  # Max panels, max turbines, max grid power

        # Define action and observation spaces
        self.action_space = spaces.Box(
            low=self.action_low,
            high=self.action_high,
            dtype=np.float32
        )

        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0]),  # Min values for state
            high=np.array([1000, 1000, 1000, 1]),  # Max values for state
            dtype=np.float32
        )

        # Emission factors (gCO2/kWh)
        self.EF_PV = 50  # Emission factor per solar panel
        self.EF_WT = 10  # Emission factor per wind turbine
        self.EF_grid = 300  # Emission factor for grid power

        # Initialize state
        self.current_state = None
        self.reset()

    def reset(self):
        """Reset the environment to an initial state."""
        self.current_state = np.array([0, 0, 1000, 0.1])  # Example initial state
        return self.current_state

    def estimate_solar_panel_cost(self, wattage, sunlight_hours_per_day, lifetime_years):
        """Estimate the cost per kWh of a solar panel over its lifetime."""
        if wattage==0: return 0
        else:
            cost_per_watt = 2.75  # Cost per watt ($/W)
            maintenance_cost_per_year = 25  # Maintenance cost ($/year)
            capital_cost = wattage * cost_per_watt  # Initial investment
            total_maintenance_cost = maintenance_cost_per_year * lifetime_years
            total_cost = capital_cost + total_maintenance_cost
            lifetime_energy_production_kwh = (wattage * sunlight_hours_per_day * 365 * lifetime_years) / 1000
            return total_cost / lifetime_energy_production_kwh  # Cost per kWh

    def estimate_wind_turbine_cost(self, rated_power_kw, capacity_factor, lifetime_years):
        """Estimate the cost per kWh of a wind turbine over its lifetime."""
        if rated_power_kw==0: return 0
        else:
            cost_per_kw = 1500  # Cost per kW ($/kW)
            maintenance_cost_per_year = 50  # Maintaenance cost ($/year)
            capital_cost = rated_power_kw * cost_per_kw  # Initial investment
            total_maintenance_cost = maintenance_cost_per_year * lifetime_years
            total_cost = capital_cost + total_maintenance_cost
            lifetime_energy_production_kwh = rated_power_kw * capacity_factor * 24 * 365 * lifetime_years
            return total_cost / lifetime_energy_production_kwh  # Cost per kWh

    def step(self, action):
        """Execute one time step in the environment."""
        # Extract action components
        N_pv = int(action[0])  # Number of PV panels (integer)
        N_wt = int(action[1])  # Number of wind turbines (integer)
        P_grid_action = action[2]  # Grid power (continuous)

        # Extract current state
        P_solar, P_wind, energy_demand, grid_price = self.current_state

        # Compute energy generated (with efficiency)
        P_pv = N_pv * P_solar * 0.2  # 20% efficiency for solar
        P_wt = N_wt * P_wind * 0.5  # 50% efficiency for wind
        total_renewable_energy = P_pv + P_wt

        # Compute energy deficit and grid usage
        energy_deficit = max(0, energy_demand - total_renewable_energy)
        grid_power_used = min(P_grid_action, energy_deficit)

        # Compute costs
        solar_cost = self.estimate_solar_panel_cost(N_pv * 300, 5, 25)  # 300W panels, 5h sunlight/day
        wind_cost = self.estimate_wind_turbine_cost(N_wt * 10000, 0.35, 25)  # 10kW turbines, 35% capacity
        grid_cost = grid_power_used * grid_price
        total_cost = solar_cost + wind_cost + grid_cost

        # Compute carbon footprint
        carbon_footprint = (
            (self.EF_PV * N_pv) +
            (self.EF_WT * N_wt) +
            (self.EF_grid * grid_power_used)
        )

        # Compute reward (negative cost and emissions)
        reward = - (total_cost + carbon_footprint)

        # Update state with random fluctuations
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

        return next_state, reward, done, {}

        