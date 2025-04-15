/**
 * Point d'entrée principal de l'application
 */

// État global de l'application
const appState = {
  solarData: null,
  windData: null,
  gridData: null,
  rlDecision: null,
  updateInterval: 500 // Intervalle de mise à jour en ms
};

/**
* Initialise l'application
*/
function initApp() {
  console.log('Initialisation de l\'application...');
  
  // Initialiser l'API si en mode simulation
  if (API.simulationMode) {
      API.initSimulation();
  }
  
  // Initialiser l'interface utilisateur
  UI.init();
  
  // Charger les données initiales
  updateData();
  
  // Configurer les mises à jour périodiques
  setInterval(updateData, appState.updateInterval);
}

/**
* Met à jour toutes les données
*/
async function updateData() {
  console.log('Mise à jour des données...');
  
  // Mettre à jour la simulation si activée
  if (API.simulationMode) {
      API.updateSimulation();
  }
  
  // Récupérer les données des capteurs
  const [solarData, windData, gridData] = await Promise.all([
      API.getSolarPower(),
      API.getWindPower(),
      API.getGridConsumption()
  ]);
  
  // Stocker les données dans l'état
  appState.solarData = solarData;
  appState.windData = windData;
  appState.gridData = gridData;
  
  // Mettre à jour l'interface utilisateur
  UI.updateSolarData(solarData);
  UI.updateWindData(windData);
  UI.updateGridData(gridData);
  UI.updateTimestamp();
  
  // Récupérer la décision de l'agent RL
  const rlDecision = await API.getRLDecision({
      solar: solarData,
      wind: windData,
      grid: gridData
  });
  
  // Stocker la décision dans l'état
  appState.rlDecision = rlDecision;
  
  // Mettre à jour l'interface avec la décision
  UI.updateRLDecision(rlDecision);
  
  // Récupérer et mettre à jour l'historique
  const powerHistory = API.getPowerHistory();
  UI.updatePowerChart(powerHistory);
}

// Attendre le chargement complet du DOM avant d'initialiser l'application
document.addEventListener('DOMContentLoaded', initApp);