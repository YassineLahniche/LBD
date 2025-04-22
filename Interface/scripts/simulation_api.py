import sys
import os
import json
import numpy as np
import random
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

# Import the Utils modules
from Utils.Env import HybridEnergyEnv
from Utils.best_action import get_best_actions

app = Flask(__name__)
CORS(app)

# Load the trained model
try:
    model_path = os.path.join(parent_dir, "Models", "agent_model.pbz2")
    agent = joblib.load(model_path)
    print(f"Model loaded successfully from {model_path}")
except Exception as e:
    print(f"Error loading model: {e}")
    agent = None

# Initialize environment
env = HybridEnergyEnv()

@app.route('/api/simulation', methods=['POST'])
def run_simulation():
    try:
        data = request.json
        simulation_time = int(data.get('simulationTime', 24))
        energy_demand = float(data.get('energyDemand', 100))
        grid_price = float(data.get('gridPrice', 0.15))
        
        # Simulation results
        simulation_results = []
        
        # Initial state
        state = env.reset()
        # Override demand and grid price
        state[2] = energy_demand
        state[3] = grid_price
        
        # Generate solar and wind patterns for the simulation period
        # More realistic day/night pattern for solar
        solar_pattern = []
        for hour in range(simulation_time):
            # Simulate day/night cycle for solar (peak at noon)
            time_of_day = hour % 24
            if time_of_day >= 6 and time_of_day <= 18:  # Daylight hours
                # Peak at noon (hour 12)
                peak_factor = 1 - abs(time_of_day - 12) / 6
                solar_factor = 0.1 + 0.8 * peak_factor  # Scale between 0.1 and 0.9
            else:
                solar_factor = 0.05  # Minimal at night
            
            solar_pattern.append(solar_factor)
        
        # Wind pattern with some variability
        wind_pattern = []
        wind_base = 0.3
        for hour in range(simulation_time):
            # Wind has less predictable pattern
            wind_factor = max(0.1, min(0.9, wind_base + np.random.normal(0, 0.15)))
            wind_pattern.append(wind_factor)
            # Gradually change base wind for next hour (smoother transitions)
            wind_base = 0.7 * wind_base + 0.3 * wind_factor
        
        # Run simulation
        total_cost = 0
        total_co2 = 0
        pv_counts = []
        wt_counts = []
        grid_powers = []
        
        for hour in range(simulation_time):
            # Update state with patterns
            state[0] = solar_pattern[hour]  # Solar factor
            state[1] = wind_pattern[hour]   # Wind factor
            
            if agent:
                # Get best action using the trained agent
                best_actions = get_best_actions(agent, [state])
                action = best_actions[tuple(state)]
            else:
                # Fallback to a simple heuristic if no agent is available
                pv_panels = int(300 * solar_pattern[hour])  # Scale with solar factor
                wt_turbines = int(50 * wind_pattern[hour])  # Scale with wind factor
                renewable_energy = (pv_panels * state[0]) + (wt_turbines * state[1])
                grid_power = max(0, energy_demand - renewable_energy)
                action = (pv_panels, wt_turbines, grid_power)
            
            # Extract action components
            pv_count, wt_count, grid_power = action
            
            # Calculate actual power generation
            pv_power = pv_count * state[0]  # Solar capacity factor
            wt_power = wt_count * state[1]  # Wind capacity factor
            total_energy = pv_power + wt_power + grid_power
            
            # Calculate cost and emissions
            cost = -env.calculate_cost(action, state)  # Negate because the function returns negative cost
            co2 = -env.calculate_co2(action, state)    # Negate because the function returns negative emissions
            
            # Accumulate totals
            total_cost += cost
            total_co2 += co2
            pv_counts.append(pv_count)
            wt_counts.append(wt_count)
            grid_powers.append(grid_power)
            
            # Record the results for this hour
            result = {
                'hour': hour,
                'solarFactor': round(state[0], 2),
                'windFactor': round(state[1], 2),
                'pvPanels': pv_count,
                'windTurbines': wt_count, 
                'gridPower': round(grid_power, 2),
                'totalEnergy': round(total_energy, 2),
                'cost': round(cost, 2),
                'co2': round(co2, 2)
            }
            simulation_results.append(result)
            
            # Simulate transition to next state (without using env.step to avoid internal random changes)
            if hour < simulation_time - 1:
                state[0] = solar_pattern[hour + 1]
                state[1] = wind_pattern[hour + 1]
        
        # Calculate averages
        avg_pv = round(sum(pv_counts) / len(pv_counts))
        avg_wt = round(sum(wt_counts) / len(wt_counts))
        avg_grid = round(sum(grid_powers) / len(grid_powers), 2)
        
        # Summary data
        summary = {
            'averagePvPanels': avg_pv,
            'averageWindTurbines': avg_wt,
            'averageGridPower': avg_grid,
            'totalCost': round(total_cost, 2),
            'totalCO2': round(total_co2, 2)
        }
        
        return jsonify({
            'success': True,
            'results': simulation_results,
            'summary': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=5001)