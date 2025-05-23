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

// Create historical chart based on time range
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
                    tension: 0.1
                },
                {
                    label: 'Énergie Éolienne (kWh)',
                    data: windData,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    tension: 0.1
                },
                {
                    label: 'Réseau Électrique (kWh)',
                    data: gridData,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    tension: 0.1
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
                        text: 'Énergie (kWh)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: `Production d'Énergie (${getTimeRangeTitle(timeRange)})`,
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

// Update historical chart when time range changes
function updateHistoricalChart(timeRange) {
    const { labels, solarData, windData, gridData } = generateHistoricalData(timeRange);
    
    historicalChart.data.labels = labels;
    historicalChart.data.datasets[0].data = solarData;
    historicalChart.data.datasets[1].data = windData;
    historicalChart.data.datasets[2].data = gridData;
    historicalChart.options.plugins.title.text = `Production d'Énergie (${getTimeRangeTitle(timeRange)})`;
    
    historicalChart.update();
}

// Generate sample historical data based on time range
function generateHistoricalData(timeRange) {
    let labels = [];
    let dataPoints = 0;
    
    switch (timeRange) {
        case 'day':
            // 24 hours
            for (let i = 0; i < 24; i++) {
                labels.push(`${i}:00`);
            }
            dataPoints = 24;
            break;
        case 'week':
            // 7 days
            const days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
            for (let i = 0; i < 7; i++) {
                labels.push(days[i]);
            }
            dataPoints = 7;
            break;
        case 'month':
            // 30 days
            for (let i = 1; i <= 30; i++) {
                labels.push(`${i}`);
            }
            dataPoints = 30;
            break;
        case 'year':
            // 12 months
            const months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'];
            labels = months;
            dataPoints = 12;
            break;
    }
    
    // Generate sample data
    const solarData = [];
    const windData = [];
    const gridData = [];
    
    for (let i = 0; i < dataPoints; i++) {
        // Solar variations
        if (timeRange === 'day') {
            // Daily pattern for solar (daylight)
            solarData.push(i >= 6 && i <= 18 ? Math.random() * 5 + 2 : Math.random() * 0.5);
        } else {
            solarData.push(Math.random() * 4 + 3);
        }
        
        // Wind variations
        windData.push(Math.random() * 6 + 2);
        
        // Grid usage
        gridData.push(Math.random() * 3 + 1);
    }
    
    return { labels, solarData, windData, gridData };
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