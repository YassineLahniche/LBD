// scripts/forecast.js
const API_BASE_URL = 'http://localhost:5000/api';
const DEFAULT_LATITUDE = 48.8566;  // Paris (vous pouvez changer selon votre localisation)
const DEFAULT_LONGITUDE = 2.3522;

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

// Update the forecast display
async function updateForecastDisplay() {
    const forecastData = await fetchForecastData();
    if (!forecastData) {
        document.getElementById('forecast-container').innerHTML = '<p>Unable to load forecast data</p>';
        return;
    }

    // Create forecasts charts
    createWindPowerChart(forecastData);
    createSolarPowerChart(forecastData);
    createTemperatureChart(forecastData);
    
    // Display forecast data in a table
    displayForecastTable(forecastData);
}

// Create wind power chart
function createWindPowerChart(data) {
    const ctx = document.getElementById('wind-power-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.time.map(timestamp => new Date(timestamp).toLocaleString()),
            datasets: [{
                label: 'Wind Power (W)',
                data: data.wind_power,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Create solar power chart
function createSolarPowerChart(data) {
    const ctx = document.getElementById('solar-power-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.time.map(timestamp => new Date(timestamp).toLocaleString()),
            datasets: [{
                label: 'Solar Power (W)',
                data: data.solar_power,
                backgroundColor: 'rgba(255, 206, 86, 0.2)',
                borderColor: 'rgba(255, 206, 86, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Create temperature chart
function createTemperatureChart(data) {
    const ctx = document.getElementById('temperature-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.time.map(timestamp => new Date(timestamp).toLocaleString()),
            datasets: [{
                label: 'Temperature (°C)',
                data: data.temperature,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true
        }
    });
}

// Display forecast data in a table
function displayForecastTable(data) {
    const tableContainer = document.getElementById('forecast-table');
    
    let tableHTML = `
    <table class="forecast-table">
        <thead>
            <tr>
                <th>Date & Time</th>
                <th>Temperature (°C)</th>
                <th>Wind Speed (m/s)</th>
                <th>Solar Radiation (W/m²)</th>
                <th>Wind Power (W)</th>
                <th>Solar Power (W)</th>
            </tr>
        </thead>
        <tbody>
    `;

    // Add first 24 hours of data (can be expanded if needed)
    for (let i = 0; i < 24; i++) {
        const date = new Date(data.time[i]);
        tableHTML += `
            <tr>
                <td>${date.toLocaleString()}</td>
                <td>${data.temperature[i].toFixed(1)}</td>
                <td>${data.wind_speed[i].toFixed(1)}</td>
                <td>${data.radiation[i].toFixed(1)}</td>
                <td>${data.wind_power[i].toFixed(1)}</td>
                <td>${data.solar_power[i].toFixed(1)}</td>
            </tr>
        `;
    }

    tableHTML += '</tbody></table>';
    tableContainer.innerHTML = tableHTML;
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', () => {
    updateForecastDisplay();
    
    // Update forecast every hour
    setInterval(updateForecastDisplay, 3600000);
});