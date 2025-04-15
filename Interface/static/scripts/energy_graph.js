// Chart objects
let productionChart, consumptionChart, renewableUsageChart, savingsChart, historicalChart;

// Current time range selection
let currentTimeRange = 'day';

// Initialize all charts
function initCharts() {
    createProductionChart();
    createConsumptionChart();
    createRenewableUsageChart();
    createSavingsChart();
    createHistoricalChart(currentTimeRange);
    
    // Add event listeners for time range buttons
    document.querySelectorAll('.time-btn').forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            document.querySelectorAll('.time-btn').forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Update time range and chart
            currentTimeRange = this.getAttribute('data-range');
            updateHistoricalChart(currentTimeRange);
        });
    });
}

// Create production chart
function createProductionChart() {
    const ctx = document.getElementById('production-chart').getContext('2d');
    
    // Generate sample data
    const today = new Date();
    const labels = [];
    const solarData = [];
    const windData = [];
    
    for (let i = 0; i < 24; i++) {
        const hour = i.toString().padStart(2, '0') + ':00';
        labels.push(hour);
        
        // Solar produces more during daylight hours
        let solarValue = i >= 6 && i <= 18 ? Math.random() * 5000 + 2000 : Math.random() * 500;
        solarData.push(solarValue);
        
        // Wind can be more variable
        let windValue = Math.random() * 6000 + 1000;
        windData.push(windValue);
    }
    
    productionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Énergie Solaire (W)',
                    data: solarData,
                    backgroundColor: 'rgba(255, 206, 86, 0.2)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 2,
                    tension: 0.2
                },
                {
                    label: 'Énergie Éolienne (W)',
                    data: windData,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    tension: 0.2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Puissance (W)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Heure'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Production d\'Énergie par Source (Aujourd\'hui)',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

// Create consumption chart
function createConsumptionChart() {
    const ctx = document.getElementById('consumption-chart').getContext('2d');
    
    // Generate sample data
    const labels = [];
    const consumptionData = [];
    
    for (let i = 0; i < 24; i++) {
        const hour = i.toString().padStart(2, '0') + ':00';
        labels.push(hour);
        
        // Consumption is higher during morning and evening
        let value;
        if (i >= 6 && i <= 9) {
            // Morning peak
            value = Math.random() * 3000 + 8000;
        } else if (i >= 17 && i <= 21) {
            // Evening peak
            value = Math.random() * 4000 + 9000;
        } else {
            // Base load
            value = Math.random() * 2000 + 5000;
        }
        consumptionData.push(value);
    }
    
    consumptionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Consommation Totale (W)',
                    data: consumptionData,
                    backgroundColor: 'rgba(153, 102, 255, 0.5)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Puissance (W)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Heure'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Consommation d\'Énergie (Aujourd\'hui)',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

// Create renewable usage chart
function createRenewableUsageChart() {
    const ctx = document.getElementById('renewable-usage-chart').getContext('2d');
    
    renewableUsageChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Solaire', 'Éolien', 'Réseau'],
            datasets: [{
                data: [35, 40, 25],
                backgroundColor: [
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 99, 132, 0.7)'
                ],
                borderColor: [
                    'rgba(255, 206, 86, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Répartition des Sources d\'Énergie',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

// Create savings chart
function createSavingsChart() {
    const ctx = document.getElementById('savings-chart').getContext('2d');
    
    // Generate sample data
    const months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'];
    const savingsData = [];
    
    for (let i = 0; i < 12; i++) {
        // Simulate increasing savings over time as system optimizes
        savingsData.push(Math.round(Math.random() * 50 + 100 + i * 15));
    }
    
    savingsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Économies (€)',
                    data: savingsData,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Euros (€)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Économies Mensuelles',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

// Create historical chart based on time range with improved performance, full-width display, and continuous operation
function createHistoricalChart(timeRange) {
    const ctx = document.getElementById('historical-chart').getContext('2d');
    
    // Generate labels and data based on time range
    const { labels, solarData, windData, gridData } = generateHistoricalData(timeRange);
    
    if (historicalChart) {
        historicalChart.destroy();
    }
    
    historicalChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Énergie Solaire (kWh)',
                    data: solarData,
                    backgroundColor: 'rgba(255, 206, 86, 0.2)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 2,
                    tension: 0.1,
                    hidden: false
                },
                {
                    label: 'Énergie Éolienne (kWh)',
                    data: windData,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    tension: 0.1,
                    hidden: false
                },
                {
                    label: 'Réseau Électrique (kWh)',
                    data: gridData,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    tension: 0.1,
                    hidden: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 150 // Short animation for better performance but still visual feedback
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Énergie (kWh)'
                    }
                },
                x: {
                    grid: {
                        display: true
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        autoSkip: true,
                        maxTicksLimit: 20 // Prevent overcrowding on x-axis
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: `Production d'Énergie (${getTimeRangeTitle(timeRange)})`,
                    font: {
                        size: 18
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        boxWidth: 40,
                        padding: 10,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                }
            },
            elements: {
                point: {
                    radius: 3, // Smaller points for better performance
                    hoverRadius: 5
                },
                line: {
                    borderWidth: 2
                }
            },
            // Prevent excessive CPU usage by limiting update rate
            resizeDelay: 100,
            interaction: {
                mode: 'nearest',
                intersect: false
            }
        }
    });
    
    // Generate custom toggle buttons
    generateToggleButtons();
    
    // Set up continuous update if needed
    setupContinuousUpdates(timeRange);
}
    
// Update historical chart with debouncing and memory management
function updateHistoricalChart(timeRange) {
    if (!historicalChart) return;
    
    // Use requestAnimationFrame for better performance
    if (updateRequestId) {
        cancelAnimationFrame(updateRequestId);
    }
    
    updateRequestId = requestAnimationFrame(() => {
        const { labels, solarData, windData, gridData } = generateHistoricalData(timeRange);
        
        // Update data efficiently
        historicalChart.data.labels = labels;
        historicalChart.data.datasets[0].data = solarData;
        historicalChart.data.datasets[1].data = windData;
        historicalChart.data.datasets[2].data = gridData;
        historicalChart.options.plugins.title.text = `Production d'Énergie (${getTimeRangeTitle(timeRange)})`;
        
        // Update with reduced animation for faster rendering
        historicalChart.update('active');
        
        // Clear reference to allow garbage collection
        updateRequestId = null;
    });
}

// Generate toggle buttons for each dataset
function generateToggleButtons() {
    const legendContainer = document.getElementById('chart-legend-container');
    if (!legendContainer) return;
    
    // Clear existing buttons
    legendContainer.innerHTML = '';
    
    // Create toggle button for each dataset
    historicalChart.data.datasets.forEach((dataset, index) => {
        const button = document.createElement('button');
        button.classList.add('toggle-button');
        if (!dataset.hidden) {
            button.classList.add('active');
        }
        
        // Set button color based on dataset
        button.style.borderColor = dataset.borderColor;
        button.style.backgroundColor = dataset.hidden ? '#ffffff' : dataset.backgroundColor;
        
        // Add button text
        button.textContent = dataset.label;
        
        // Add click event
        button.addEventListener('click', () => {
            // Toggle dataset visibility
            const meta = historicalChart.getDatasetMeta(index);
            meta.hidden = !meta.hidden;
            
            // Toggle button visual state
            button.classList.toggle('active');
            button.style.backgroundColor = meta.hidden ? '#ffffff' : dataset.backgroundColor;
            
            // Save state to dataset
            dataset.hidden = meta.hidden;
            
            // Update chart
            historicalChart.update();
        });
        
        legendContainer.appendChild(button);
    });
}

// Setup continuous updates if needed
function setupContinuousUpdates(timeRange) {
    // Clear any existing interval
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    
    // Determine update frequency based on time range
    let updateFrequency;
    switch (timeRange) {
        case 'day':
            updateFrequency = 30000; // 30 seconds for day view
            break;
        case 'week':
            updateFrequency = 60000; // 1 minute for week view
            break;
        case 'month':
            updateFrequency = 300000; // 5 minutes for month view
            break;
        case 'year':
            updateFrequency = 900000; // 15 minutes for year view
            break;
        default:
            updateFrequency = 60000; // 1 minute default
    }
    
    // Set up continuous update interval
    updateInterval = setInterval(() => {
        updateHistoricalChart(timeRange);
    }, updateFrequency);
    
    // Clean up interval on page unload
    window.addEventListener('beforeunload', () => {
        if (updateInterval) {
            clearInterval(updateInterval);
        }
    });
}

// Efficient resize handler with debouncing
let resizeTimer;
let updateRequestId;
let updateInterval;

window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        if (historicalChart) {
            historicalChart.resize();
        }
    }, 100);
});

// Memory-efficient function to get time range title
function getTimeRangeTitle(timeRange) {
    const titles = {
        'day': 'Dernières 24 Heures',
        'week': 'Dernière Semaine',
        'month': 'Dernier Mois',
        'year': 'Dernière Année'
    };
    
    return titles[timeRange] || timeRange;
}

// Function to clean up resources when component unmounts or page changes
function cleanupChart() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    
    if (updateRequestId) {
        cancelAnimationFrame(updateRequestId);
    }
    
    if (historicalChart) {
        historicalChart.destroy();
        historicalChart = null;
    }
}

// Throttle function to prevent too frequent updates
function throttle(func, delay) {
    let lastCall = 0;
    return function(...args) {
        const now = new Date().getTime();
        if (now - lastCall < delay) {
            return;
        }
        lastCall = now;
        return func(...args);
    };
}

// Use throttled function for window resize
window.addEventListener('resize', throttle(() => {
    if (historicalChart) {
        historicalChart.resize();
    }
}, 100));

// Function to get a human-readable title for time range
function getTimeRangeTitle(timeRange) {
    switch (timeRange) {
        case 'day':
            return 'Dernières 24 Heures';
        case 'week':
            return 'Dernière Semaine';
        case 'month':
            return 'Dernier Mois';
        case 'year':
            return 'Dernière Année';
        default:
            return timeRange;
    }
}
// Get title based on time range
function getTimeRangeTitle(timeRange) {
    switch (timeRange) {
        case 'day': return 'Aujourd\'hui';
        case 'week': return 'Cette Semaine';
        case 'month': return 'Ce Mois';
        case 'year': return 'Cette Année';
        default: return '';
    }
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', initCharts);