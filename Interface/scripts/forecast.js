// scripts/forecast.js
const API_BASE_URL = 'http://localhost:5000/api';
const DEFAULT_LATITUDE = 33.61;
const DEFAULT_LONGITUDE = 7.65;

// Chart color schemes for consistent theme
const CHART_COLORS = {
    wind: {
        fill: 'rgba(54, 162, 235, 0.2)',
        border: 'rgba(54, 162, 235, 1)',
        pointBg: 'rgba(54, 162, 235, 1)',
        pointBorder: '#fff'
    },
    solar: {
        fill: 'rgba(255, 193, 7, 0.2)',
        border: 'rgba(255, 193, 7, 1)',
        pointBg: 'rgba(255, 193, 7, 1)',
        pointBorder: '#fff'
    },
    temperature: {
        fill: 'rgba(255, 99, 132, 0.2)',
        border: 'rgba(255, 99, 132, 1)',
        pointBg: 'rgba(255, 99, 132, 1)',
        pointBorder: '#fff'
    }
};

// Shared chart configuration
const CHART_OPTIONS = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
        duration: 1000,
        easing: 'easeOutQuart'
    },
    elements: {
        line: {
            tension: 0.4 // Smoother curve
        },
        point: {
            radius: 3,
            hoverRadius: 6
        }
    },
    plugins: {
        legend: {
            labels: {
                font: {
                    family: "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                    size: 12
                },
                boxWidth: 15,
                padding: 15
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            titleFont: {
                family: "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                size: 14,
                weight: 'bold'
            },
            bodyFont: {
                family: "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                size: 13
            },
            padding: 10,
            cornerRadius: 6,
            displayColors: true
        }
    },
    scales: {
        x: {
            grid: {
                color: 'rgba(0, 0, 0, 0.05)'
            },
            ticks: {
                font: {
                    family: "'Segoe UI', Roboto, Arial, sans-serif",
                    size: 11
                },
                maxRotation: 45,
                minRotation: 45
            }
        },
        y: {
            beginAtZero: true,
            grid: {
                color: 'rgba(0, 0, 0, 0.05)'
            },
            ticks: {
                font: {
                    family: "'Segoe UI', Roboto, Arial, sans-serif",
                    size: 11
                }
            }
        }
    }
};

// Format timestamps for better readability
function formatDateTime(timestamp) {
    const date = new Date(timestamp);
    const options = { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit'
    };
    return date.toLocaleDateString(undefined, options);
}

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
    // Add loading indicators
    document.querySelectorAll('.chart-container canvas').forEach(canvas => {
        canvas.parentNode.classList.add('loading');
    });
    document.getElementById('forecast-table').classList.add('loading');
    
    const forecastData = await fetchForecastData();
    
    // Remove loading indicators
    document.querySelectorAll('.loading').forEach(el => {
        el.classList.remove('loading');
    });
    
    if (!forecastData) {
        document.getElementById('forecast-container').innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <p>Unable to load forecast data. Please try again later.</p>
            </div>
        `;
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
    
    // Destroy existing chart if it exists
    if (window.windChart) {
        window.windChart.destroy();
    }
    
    const formattedLabels = data.time.map(timestamp => formatDateTime(timestamp));
    
    window.windChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: formattedLabels,
            datasets: [{
                label: 'Wind Power (W)',
                data: data.wind_power,
                backgroundColor: CHART_COLORS.wind.fill,
                borderColor: CHART_COLORS.wind.border,
                pointBackgroundColor: CHART_COLORS.wind.pointBg,
                pointBorderColor: CHART_COLORS.wind.pointBorder,
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            ...CHART_OPTIONS,
            plugins: {
                ...CHART_OPTIONS.plugins,
                title: {
                    display: true,
                    text: 'Wind Power Generation Forecast',
                    font: {
                        family: "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                }
            }
        }
    });
}

// Create solar power chart
function createSolarPowerChart(data) {
    const ctx = document.getElementById('solar-power-chart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.solarChart) {
        window.solarChart.destroy();
    }
    
    const formattedLabels = data.time.map(timestamp => formatDateTime(timestamp));
    
    window.solarChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: formattedLabels,
            datasets: [{
                label: 'Solar Power (W)',
                data: data.solar_power,
                backgroundColor: CHART_COLORS.solar.fill,
                borderColor: CHART_COLORS.solar.border,
                pointBackgroundColor: CHART_COLORS.solar.pointBg,
                pointBorderColor: CHART_COLORS.solar.pointBorder,
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            ...CHART_OPTIONS,
            plugins: {
                ...CHART_OPTIONS.plugins,
                title: {
                    display: true,
                    text: 'Solar Power Generation Forecast',
                    font: {
                        family: "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                }
            }
        }
    });
}

// Create temperature chart
function createTemperatureChart(data) {
    const ctx = document.getElementById('temperature-chart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.temperatureChart) {
        window.temperatureChart.destroy();
    }
    
    const formattedLabels = data.time.map(timestamp => formatDateTime(timestamp));
    
    window.temperatureChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: formattedLabels,
            datasets: [{
                label: 'Temperature (°C)',
                data: data.temperature,
                backgroundColor: CHART_COLORS.temperature.fill,
                borderColor: CHART_COLORS.temperature.border,
                pointBackgroundColor: CHART_COLORS.temperature.pointBg,
                pointBorderColor: CHART_COLORS.temperature.pointBorder,
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            ...CHART_OPTIONS,
            plugins: {
                ...CHART_OPTIONS.plugins,
                title: {
                    display: true,
                    text: 'Temperature Forecast',
                    font: {
                        family: "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                }
            }
        }
    });
}

// Display forecast data in a table
function displayForecastTable(data) {
    const tableContainer = document.getElementById('forecast-table');
    
    // Create table header
    let tableHTML = `
    <div class="forecast-table-wrapper">
        <h3 class="table-title">Detailed Forecast Data</h3>
        <div class="table-scroll">
            <table class="forecast-table">
                <thead>
                    <tr>
                        <th>Date & Time</th>
                        <th>Temperature (°C)</th>
                        <th>Wind Speed (m/s)</th>
                        <th>Solar Radiation (W/m²)</th>
                        <th>Wind Power (W)</th>
                        <th>Solar Power (W)</th>
                        <th>Total Power (W)</th>
                    </tr>
                </thead>
                <tbody>
    `;

    // Add data rows with enhanced formatting
    for (let i = 0; i < 24; i++) {
        const date = new Date(data.time[i]);
        const totalPower = data.wind_power[i] + data.solar_power[i];
        
        // Add zebra striping and hover effects with CSS classes
        const rowClass = i % 2 === 0 ? 'even-row' : 'odd-row';
        
        tableHTML += `
            <tr class="${rowClass}">
                <td>${date.toLocaleString(undefined, {
                    weekday: 'short',
                    month: 'short', 
                    day: 'numeric',
                    hour: '2-digit', 
                    minute: '2-digit'
                })}</td>
                <td>${data.temperature[i].toFixed(1)} °C</td>
                <td>${data.wind_speed[i].toFixed(1)} m/s</td>
                <td>${data.radiation[i].toFixed(1)} W/m²</td>
                <td>${data.wind_power[i].toFixed(1)} W</td>
                <td>${data.solar_power[i].toFixed(1)} W</td>
                <td>${totalPower.toFixed(1)} W</td>
            </tr>
        `;
    }

    tableHTML += `
                </tbody>
            </table>
        </div>
        <div class="table-footer">
            <p>Forecast updated: ${new Date().toLocaleString()}</p>
        </div>
    </div>`;
    
    tableContainer.innerHTML = tableHTML;
    
    // Add download data button
    const downloadBtn = document.createElement('button');
    downloadBtn.className = 'download-btn';
    downloadBtn.innerHTML = '<i class="fas fa-download"></i> Export Data';
    downloadBtn.addEventListener('click', () => exportTableData(data));
    tableContainer.querySelector('.table-footer').appendChild(downloadBtn);
}

// Export table data as CSV
function exportTableData(data) {
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Date,Temperature (°C),Wind Speed (m/s),Solar Radiation (W/m²),Wind Power (W),Solar Power (W),Total Power (W)\n";
    
    for (let i = 0; i < data.time.length; i++) {
        const date = new Date(data.time[i]).toISOString();
        const totalPower = data.wind_power[i] + data.solar_power[i];
        
        csvContent += `${date},${data.temperature[i]},${data.wind_speed[i]},${data.radiation[i]},${data.wind_power[i]},${data.solar_power[i]},${totalPower}\n`;
    }
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `forecast_data_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Add CSS for better styling
    const style = document.createElement('style');
    style.textContent = `
        .chart-container {
            position: relative;
            height: 300px;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            padding: 15px;
            background-color: #fff;
        }
        
        .chart-container.loading::after {
            content: "Loading...";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 16px;
            color: #666;
        }
        
        .forecast-table-wrapper {
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            background-color: #fff;
            margin-bottom: 30px;
        }
        
        .table-title {
            padding: 15px 20px;
            margin: 0;
            background-color: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            font-size: 16px;
            font-weight: bold;
            color: #333;
        }
        
        .table-scroll {
            overflow-x: auto;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .forecast-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .forecast-table th {
            background-color: #f8f9fa;
            position: sticky;
            top: 0;
            box-shadow: 0 1px 0 rgba(0, 0, 0, 0.1);
            padding: 12px 15px;
            text-align: left;
            font-size: 14px;
            font-weight: 600;
            color: #333;
        }
        
        .forecast-table td {
            padding: 10px 15px;
            font-size: 14px;
            border-bottom: 1px solid #eee;
        }
        
        .forecast-table .even-row {
            background-color: #fff;
        }
        
        .forecast-table .odd-row {
            background-color: #f9f9f9;
        }
        
        .forecast-table tr:hover {
            background-color: #f2f8ff !important;
        }
        
        .table-footer {
            padding: 15px 20px;
            background-color: #f8f9fa;
            border-top: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
            color: #666;
        }
        
        .download-btn {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: background-color 0.3s;
        }
        
        .download-btn:hover {
            background-color: #45a049;
        }
        
        .error-message {
            background-color: #fff3f3;
            border-left: 4px solid #f44336;
            padding: 15px 20px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .error-message i {
            color: #f44336;
            font-size: 24px;
            margin-right: 15px;
        }
    `;
    document.head.appendChild(style);
    
    // Load Font Awesome if not already loaded
    if (!document.querySelector('link[href*="font-awesome"]')) {
        const fontAwesome = document.createElement('link');
        fontAwesome.rel = 'stylesheet';
        fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
        document.head.appendChild(fontAwesome);
    }
    
    updateForecastDisplay();
    
    // Update forecast every hour
    setInterval(updateForecastDisplay, 3600000);
});