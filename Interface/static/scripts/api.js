// Configuration API
const API_BASE_URL = 'http://localhost:5000/api';
const DEFAULT_LATITUDE = 33.61;  // Paris (à modifier selon votre localisation)
const DEFAULT_LONGITUDE = 7.65;

// API object for the app.js to use
const API = {
    simulationMode: true, // True pour le mode simulation, False pour utiliser de vraies données
    
    // Initialize simulation data
    initSimulation: function() {
        this.simulatedData = {
            solar: 0,
            wind: 0,
            grid: 0,
            history: {
                timestamps: [],
                solar: [],
                wind: [],
                grid: []
            },
            weather: {
                temperature: 22,
                windSpeed: 4.5,
                solarRadiation: 650
            }
        };
        console.log('Simulation initialized');
    },
    
    // Update simulation with random variations
    updateSimulation: function() {
        // Add timestamp
        const now = new Date();
        this.simulatedData.history.timestamps.push(now);
        
        // Generate random values with some realism
        const hour = now.getHours();
        
        // Solar power depends on time of day
        let solarPower = hour >= 7 && hour <= 19 
            ? Math.random() * 3000 + 1000
            : Math.random() * 500;
        
        // Wind varies more randomly
        let windPower = Math.random() * 4000 + 500;
        
        // Grid consumption varies
        let gridPower = Math.random() * 5000 + 3000;
        
        // Store current values
        this.simulatedData.solar = solarPower;
        this.simulatedData.wind = windPower;
        this.simulatedData.grid = gridPower;
        
        // Store in history (keep last 50 values)
        this.simulatedData.history.solar.push(solarPower);
        this.simulatedData.history.wind.push(windPower);
        this.simulatedData.history.grid.push(gridPower);
        
        if (this.simulatedData.history.timestamps.length > 50) {
            this.simulatedData.history.timestamps.shift();
            this.simulatedData.history.solar.shift();
            this.simulatedData.history.wind.shift();
            this.simulatedData.history.grid.shift();
        }
        
        // Update weather
        this.simulatedData.weather = {
            temperature: 20 + Math.random() * 5,
            windSpeed: 3 + Math.random() * 4,
            solarRadiation: hour >= 7 && hour <= 19 ? 500 + Math.random() * 300 : Math.random() * 100
        };
        
        console.log('Simulation updated', this.simulatedData);
    },
    
    // Get solar power
    getSolarPower: async function() {
        if (this.simulationMode) {
            return this.simulatedData.solar;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/sensor/solar`);
            const data = await response.json();
            return data.power;
        } catch (error) {
            console.error('Error fetching solar power:', error);
            return 0;
        }
    },
    
    // Get wind power
    getWindPower: async function() {
        if (this.simulationMode) {
            return this.simulatedData.wind;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/sensor/wind`);
            const data = await response.json();
            return data.power;
        } catch (error) {
            console.error('Error fetching wind power:', error);
            return 0;
        }
    },
    
    // Get grid consumption
    getGridConsumption: async function() {
        if (this.simulationMode) {
            return this.simulatedData.grid;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/sensor/grid`);
            const data = await response.json();
            return data.power;
        } catch (error) {
            console.error('Error fetching grid consumption:', error);
            return 0;
        }
    },
    
    // Get weather data
    getWeatherData: async function() {
        if (this.simulationMode) {
            return this.simulatedData.weather;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/weather/current`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching weather data:', error);
            return {
                temperature: 0,
                windSpeed: 0,
                solarRadiation: 0
            };
        }
    },
    
    // Get RL decision
    getRLDecision: async function(data) {
        if (this.simulationMode) {
            const totalPower = data.solar + data.wind + data.grid;
            const totalNeeded = totalPower * 0.9; // Simulation needs
            
            // Prioritize renewable sources
            const solarUse = Math.min(data.solar, totalNeeded * 0.5);
            const remaining = totalNeeded - solarUse;
            const windUse = Math.min(data.wind, remaining * 0.7);
            const gridUse = totalNeeded - solarUse - windUse;
            
            return {
                solar: solarUse,
                wind: windUse,
                grid: gridUse,
                explanation: `
                    <h4>Décision de l'agent RL</h4>
                    <p>Basé sur les données actuelles, l'agent RL a alloué:</p>
                    <ul>
                        <li>${Math.round(solarUse)} W d'énergie solaire (${Math.round(solarUse/totalNeeded*100)}%)</li>
                        <li>${Math.round(windUse)} W d'énergie éolienne (${Math.round(windUse/totalNeeded*100)}%)</li>
                        <li>${Math.round(gridUse)} W du réseau (${Math.round(gridUse/totalNeeded*100)}%)</li>
                    </ul>
                    <p>Cette décision a été prise en considérant l'ensoleillement actuel, la vitesse du vent et la demande en énergie.</p>
                `
            };
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/rl/decision`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Error getting RL decision:', error);
            return {
                solar: 0,
                wind: 0,
                grid: 0,
                explanation: "Impossible de récupérer la décision de l'agent RL."
            };
        }
    },
    
    // Get power history
    getPowerHistory: function() {
        if (this.simulationMode) {
            return {
                timestamps: this.simulatedData.history.timestamps,
                solar: this.simulatedData.history.solar,
                wind: this.simulatedData.history.wind,
                grid: this.simulatedData.history.grid
            };
        }
        
        // Implement real API call later
        return {
            timestamps: [],
            solar: [],
            wind: [],
            grid: []
        };
    }
};

// Fetch forecast data from our API
async function fetchForecastData(latitude = DEFAULT_LATITUDE, longitude = DEFAULT_LONGITUDE) {
    try {
        const response = await fetch(`${API_BASE_URL}/forecast/${latitude}/${longitude}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching forecast data:', error);
        return null;
    }
}

// Fetch current weather data
async function fetchCurrentData(latitude = DEFAULT_LATITUDE, longitude = DEFAULT_LONGITUDE) {
    try {
        const response = await fetch(`${API_BASE_URL}/current/${latitude}/${longitude}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching current data:', error);
        return null;
    }
}

// Simulate getting sensor data (à remplacer par une vraie API de capteurs)
async function fetchSensorData() {
    // Simulation de données de capteurs
    return {
        solar_power: Math.random() * 5000,  // 0-5kW
        wind_power: Math.random() * 10000,  // 0-10kW
        grid_power: Math.random() * 8000,   // 0-8kW
        total_load: Math.random() * 15000 + 5000  // 5-20kW
    };
}

// Simulate RL agent decision (à remplacer par votre vrai agent)
async function getOptimalAllocation(sensorData, weatherData) {
    // Simulation de décision de l'agent RL
    const totalAvailable = sensorData.solar_power + sensorData.wind_power + sensorData.grid_power;
    const totalLoad = sensorData.total_load;
    
    // Stratégie simple: utiliser d'abord l'énergie renouvelable
    let solarAllocation = Math.min(sensorData.solar_power, totalLoad * 0.4);
    let remainingLoad = totalLoad - solarAllocation;
    
    let windAllocation = Math.min(sensorData.wind_power, remainingLoad * 0.7);
    remainingLoad -= windAllocation;
    
    let gridAllocation = Math.min(sensorData.grid_power, remainingLoad);
    
    return {
        solar: solarAllocation,
        wind: windAllocation,
        grid: gridAllocation,
        explanation: `
            Basé sur les conditions météorologiques actuelles, l'agent RL a alloué:
            - ${Math.round(solarAllocation)} W d'énergie solaire (${Math.round(solarAllocation/totalLoad*100)}%)
            - ${Math.round(windAllocation)} W d'énergie éolienne (${Math.round(windAllocation/totalLoad*100)}%)
            - ${Math.round(gridAllocation)} W du réseau électrique (${Math.round(gridAllocation/totalLoad*100)}%)
            
            Cette décision optimise l'utilisation des énergies renouvelables disponibles tout en assurant une alimentation stable.
        `
    };
}