// UI management object
const UI = {
    // Chart object references
    charts: {
        allocation: null
    },
    
    // Initialize UI
    init: function() {
        console.log('Initializing UI...');
        
        // Initialize allocation chart
        this.initAllocationChart();
        
        // Set initial message
        document.getElementById('ai-explanation').innerHTML = 
            '<p>En attente des données pour générer une allocation...</p>';
    },
    
    // Initialize allocation chart
    initAllocationChart: function() {
        const ctx = document.getElementById('allocation-chart').getContext('2d');
        this.charts.allocation = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Énergie Solaire', 'Énergie Éolienne', 'Réseau Électrique'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: [
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
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
                maintainAspectRatio: false
            }
        });
    },
    
    // Update solar power display
    updateSolarData: function(power) {
        // Update power value display
        document.getElementById('solar-power').textContent = `${Math.round(power)} W`;
        
        // Update meter (assuming max 5000W)
        const meter = document.getElementById('solar-meter');
        const percentage = Math.min(Math.round((power / 5000) * 100), 100);
        meter.style.width = `${percentage}%`;
        
        // Update color based on percentage
        if (percentage > 70) {
            meter.style.backgroundColor = '#4CAF50'; // Green for high production
        } else if (percentage > 30) {
            meter.style.backgroundColor = '#FFC107'; // Yellow for medium
        } else {
            meter.style.backgroundColor = '#F44336'; // Red for low
        }
    },
    
    // Update wind power display
    updateWindData: function(power) {
        // Update power value display
        document.getElementById('wind-power').textContent = `${Math.round(power)} W`;
        
        // Update meter (assuming max 10000W)
        const meter = document.getElementById('wind-meter');
        const percentage = Math.min(Math.round((power / 10000) * 100), 100);
        meter.style.width = `${percentage}%`;
        
        // Update color based on percentage
        if (percentage > 70) {
            meter.style.backgroundColor = '#4CAF50'; // Green for high production
        } else if (percentage > 30) {
            meter.style.backgroundColor = '#FFC107'; // Yellow for medium
        } else {
            meter.style.backgroundColor = '#F44336'; // Red for low
        }
    },
    
    // Update grid power display
    updateGridData: function(power) {
        // Update power value display
        document.getElementById('grid-power').textContent = `${Math.round(power)} W`;
        
        // Update meter (assuming max 10000W)
        const meter = document.getElementById('grid-meter');
        const percentage = Math.min(Math.round((power / 10000) * 100), 100);
        meter.style.width = `${percentage}%`;
    },
    
    // Update weather data
    updateWeatherData: function(weatherData) {
        document.getElementById('temperature').textContent = `${weatherData.temperature.toFixed(1)}°C`;
        document.getElementById('wind-speed').textContent = `${weatherData.windSpeed.toFixed(1)} m/s`;
        document.getElementById('solar-radiation').textContent = `${Math.round(weatherData.solarRadiation)} W/m²`;
    },
    
    // Update RL decision display
    updateRLDecision: function(decision) {
        // Update chart
        if (this.charts.allocation) {
            this.charts.allocation.data.datasets[0].data = [
                decision.solar,
                decision.wind,
                decision.grid
            ];
            this.charts.allocation.update();
        }
        
        // Update explanation
        document.getElementById('ai-explanation').innerHTML = decision.explanation;
    },
    
    // Update timestamp
    updateTimestamp: function() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        const dateString = now.toLocaleDateString();
        
        // Ajouter un élément de timestamp s'il n'existe pas
        let timestampEl = document.getElementById('data-timestamp');
        if (!timestampEl) {
            timestampEl = document.createElement('div');
            timestampEl.id = 'data-timestamp';
            timestampEl.classList.add('timestamp');
            document.querySelector('#real-time-data').appendChild(timestampEl);
        }
        
        timestampEl.textContent = `Dernière mise à jour: ${timeString} ${dateString}`;
    },
    
    // Update power history chart
    updatePowerChart: function(historyData) {
        // Check if chart container exists
        const chartContainer = document.getElementById('power-history-chart');
        if (!chartContainer) {
            console.log('Power history chart container not found');
            return;
        }
        
        // Initialize chart if not exists
        if (!this.charts.powerHistory) {
            const ctx = chartContainer.getContext('2d');
            this.charts.powerHistory = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: historyData.timestamps.map(ts => 
                        new Date(ts).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
                    ),
                    datasets: [
                        {
                            label: 'Énergie Solaire (W)',
                            data: historyData.solar,
                            borderColor: 'rgba(255, 206, 86, 1)',
                            backgroundColor: 'rgba(255, 206, 86, 0.2)',
                            borderWidth: 2,
                            tension: 0.1
                        },
                        {
                            label: 'Énergie Éolienne (W)',
                            data: historyData.wind,
                            borderColor: 'rgba(54, 162, 235, 1)',
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderWidth: 2,
                            tension: 0.1
                        },
                        {
                            label: 'Réseau Électrique (W)',
                            data: historyData.grid,
                            borderColor: 'rgba(255, 99, 132, 1)',
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
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
                                text: 'Puissance (W)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Heure'
                            }
                        }
                    }
                }
            });
        } else {
            // Update existing chart
            this.charts.powerHistory.data.labels = historyData.timestamps.map(ts => 
                new Date(ts).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
            );
            this.charts.powerHistory.data.datasets[0].data = historyData.solar;
            this.charts.powerHistory.data.datasets[1].data = historyData.wind;
            this.charts.powerHistory.data.datasets[2].data = historyData.grid;
            this.charts.powerHistory.update();
        }
    }
};