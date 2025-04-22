// Charts for displaying simulation results
let energyAllocationChart = null;
let costEmissionsChart = null;

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Initialize empty charts
    initializeCharts();
    
    // Add event listener to the simulation button
    document.getElementById('start-simulation').addEventListener('click', runSimulation);
});

// Initialize the charts with empty data
function initializeCharts() {
    // Energy allocation chart
    const energyAllocationCtx = document.getElementById('energy-allocation-chart').getContext('2d');
    energyAllocationChart = new Chart(energyAllocationCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Énergie Solaire',
                    data: [],
                    borderColor: '#FFD700',
                    backgroundColor: 'rgba(255, 215, 0, 0.2)',
                    fill: true
                },
                {
                    label: 'Énergie Éolienne',
                    data: [],
                    borderColor: '#4BC0C0',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true
                },
                {
                    label: 'Énergie du Réseau',
                    data: [],
                    borderColor: '#FF6384',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Heure'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Énergie (kW)'
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Allocation d\'Énergie par Source'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });

    // Cost and emissions chart
    const costEmissionsCtx = document.getElementById('cost-emissions-chart').getContext('2d');
    costEmissionsChart = new Chart(costEmissionsCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Coût (€)',
                    data: [],
                    borderColor: '#36A2EB',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    yAxisID: 'y'
                },
                {
                    label: 'Émissions CO2 (kg)',
                    data: [],
                    borderColor: '#FF9F40',
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Heure'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Coût (€)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Émissions CO2 (kg)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Coût et Émissions par Heure'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

// Run the simulation
async function runSimulation() {
    try {
        // Show loading state
        const startButton = document.getElementById('start-simulation');
        startButton.textContent = 'Simulation en cours...';
        startButton.disabled = true;
        
        // Get simulation parameters
        const simulationTime = document.getElementById('simulation-time').value;
        const energyDemand = document.getElementById('energy-demand').value;
        const gridPrice = document.getElementById('grid-price').value;
        
        // Call the simulation API
        const response = await fetch('http://localhost:5001/api/simulation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                simulationTime: parseInt(simulationTime),
                energyDemand: parseFloat(energyDemand),
                gridPrice: parseFloat(gridPrice)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update charts and display results
            updateChartsWithData(data.results);
            updateSummaryStats(data.summary);
            populateResultsTable(data.results);
        } else {
            alert('Erreur lors de la simulation: ' + data.error);
        }
    } catch (error) {
        console.error('Error running simulation:', error);
        alert('Erreur de connexion au serveur de simulation. Assurez-vous que le serveur est en cours d\'exécution.');
    } finally {
        // Reset button state
        const startButton = document.getElementById('start-simulation');
        startButton.textContent = 'Démarrer la Simulation';
        startButton.disabled = false;
    }
}

// Update charts with simulation data
function updateChartsWithData(results) {
    // Prepare data for charts
    const hours = results.map(r => r.hour);
    
    // Calculate energy values
    const solarEnergy = results.map(r => r.pvPanels * r.solarFactor);
    const windEnergy = results.map(r => r.windTurbines * r.windFactor);
    const gridEnergy = results.map(r => r.gridPower);
    
    // Cost and emissions
    const costs = results.map(r => r.cost);
    const emissions = results.map(r => r.co2);
    
    // Update energy allocation chart
    energyAllocationChart.data.labels = hours;
    energyAllocationChart.data.datasets[0].data = solarEnergy;
    energyAllocationChart.data.datasets[1].data = windEnergy;
    energyAllocationChart.data.datasets[2].data = gridEnergy;
    energyAllocationChart.update();
    
    // Update cost and emissions chart
    costEmissionsChart.data.labels = hours;
    costEmissionsChart.data.datasets[0].data = costs;
    costEmissionsChart.data.datasets[1].data = emissions;
    costEmissionsChart.update();
}

// Update summary statistics
function updateSummaryStats(summary) {
    document.getElementById('avg-pv-panels').textContent = summary.averagePvPanels;
    document.getElementById('avg-wind-turbines').textContent = summary.averageWindTurbines;
    document.getElementById('avg-grid-power').textContent = summary.averageGridPower + ' kW';
    document.getElementById('total-cost').textContent = summary.totalCost + ' €';
    document.getElementById('total-co2').textContent = summary.totalCO2 + ' kg';
}

// Populate the detailed results table
function populateResultsTable(results) {
    const tableBody = document.querySelector('#simulation-data-table tbody');
    tableBody.innerHTML = '';
    
    results.forEach(result => {
        const row = document.createElement('tr');
        
        // Calculate actual energy values
        const solarEnergy = (result.pvPanels * result.solarFactor).toFixed(2);
        const windEnergy = (result.windTurbines * result.windFactor).toFixed(2);
        
        row.innerHTML = `
            <td>${result.hour}</td>
            <td>${result.solarFactor}</td>
            <td>${result.windFactor}</td>
            <td>${result.pvPanels} (${solarEnergy} kW)</td>
            <td>${result.windTurbines} (${windEnergy} kW)</td>
            <td>${result.gridPower} kW</td>
            <td>${result.totalEnergy} kW</td>
            <td>${result.cost} €</td>
            <td>${result.co2} kg</td>
        `;
        
        tableBody.appendChild(row);
    });
}