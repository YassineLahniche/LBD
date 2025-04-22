# Système de Gestion Intelligente d'Énergie Renouvelable

Un système intelligent utilisant l'apprentissage par renforcement pour optimiser l'allocation d'énergie renouvelable en temps réel.

## À propos

Ce projet est une interface web interactive qui permet de suivre, analyser et optimiser l'utilisation des sources d'énergies renouvelables (solaire et éolienne) en temps réel. À l'aide d'un agent d'apprentissage par renforcement (RL), le système prend des décisions optimales sur l'allocation d'énergie en fonction des conditions météorologiques actuelles et prévues.

## Fonctionnalités principales

- **Tableau de bord en temps réel** : Visualisation des données de production d'énergie solaire et éolienne ainsi que de la consommation du réseau
- **Prise de décision intelligente** : Algorithme d'apprentissage par renforcement qui optimise l'allocation d'énergie
- **Prévisions météorologiques** : Intégration avec l'API Open-Meteo pour obtenir des prévisions précises et calculer la production potentielle
- **Graphiques d'analyse** : Visualisation détaillée des données historiques de production et consommation
- **Interface réactive** : Design moderne qui s'adapte aux différentes tailles d'écran

## Prérequis

- Navigateur web moderne (Chrome, Firefox, Safari, Edge)
- Python 3.7+ pour l'API backend
- Connexion internet pour les données météorologiques en temps réel

## Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/username/gestion-energie-renouvelable.git
   cd gestion-energie-renouvelable
   ```

2. **Installer les dépendances Python**
   ```bash
   pip install flask flask-cors requests numpy
   ```

4. **Ouvrir l'application**
   
   ```bash
   python app.py
   ```
## Structure du projet

```
.
├── assets/
│   └── icons/              # Icônes SVG pour l'interface
│       ├── grid.svg        # Icône du réseau électrique
│       ├── solar.svg       # Icône solaire
│       └── wind.svg        # Icône éolienne
├── scripts/
│   ├── api.js              # Interface avec l'API backend
│   ├── app.js              # Point d'entrée principal de l'application
│   ├── forecast.js         # Gestion des prévisions météorologiques
│   ├── energy-graph.js     # Graphiques d'analyse énergétique
│   └── ui.js               # Gestion de l'interface utilisateur
├── style/
│   └── main.css            # Styles de l'application
├── weather_api.py          # API backend pour les données météo et calculs
├── index.html              # Page principale du tableau de bord
├── forecast.html           # Page des prévisions météorologiques
├── energy-graph.html       # Page des graphiques d'analyse
└── README.md               # Documentation du projet
```

## Personnalisation

### Configuration des sources d'énergie

Vous pouvez ajuster les paramètres des sources d'énergie dans le fichier `weather_api.py`:

```python
# Constantes pour les calculs d'énergie
TURBINE_RADIUS = 5  # Rayon des turbines éoliennes en mètres
EFFICIENCY_WIND = 0.4  # Efficacité des turbines (40%)
EFFICIENCY_SOLAR = 0.2  # Efficacité des panneaux solaires (20%)
```

### Emplacement géographique

Par défaut, le système utilise les coordonnées géographiques (33.61, 7.65). Vous pouvez modifier cet emplacement via l'interface utilisateur dans la page des prévisions.

## Fonctionnement technique

### Calcul de l'énergie éolienne

La puissance éolienne est calculée selon la formule:

```
P = 0.5 × ρ × A × v³ × η
```

Où:
- P est la puissance générée (W)
- ρ est la densité de l'air (kg/m³)
- A est la surface balayée par les pales (m²)
- v est la vitesse du vent (m/s)
- η est l'efficacité de la turbine

### Calcul de l'énergie solaire

La puissance solaire est calculée selon la formule:

```
P = G × A × η
```

Où:
- P est la puissance générée (W)
- G est l'irradiation solaire (W/m²)
- A est la surface des panneaux (m²)
- η est l'efficacité des panneaux

### Agent d'apprentissage par renforcement

L'agent RL optimise l'allocation d'énergie en fonction:
- Des conditions météorologiques actuelles
- Des prévisions météorologiques
- De l'historique des performances
- Des coûts d'utilisation des différentes sources

## API

Le système expose les endpoints API suivants:

- `GET /api/sensor/solar` - Obtenir la production d'énergie solaire actuelle
- `GET /api/sensor/wind` - Obtenir la production d'énergie éolienne actuelle
- `GET /api/sensor/grid` - Obtenir la consommation du réseau actuelle
- `GET /api/forecast/{lat}/{lon}` - Obtenir les prévisions météorologiques et énergétiques

## Contribution

Les contributions sont les bienvenues! Pour contribuer:

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## Dépannage

### L'interface n'affiche pas les données

- Vérifiez que le serveur backend est en cours d'exécution
- Assurez-vous que votre navigateur autorise les requêtes CORS
- Vérifiez la console du navigateur pour les erreurs JavaScript

### Les données météorologiques ne se chargent pas

- Vérifiez votre connexion internet
- Assurez-vous que l'API Open-Meteo est accessible

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue sur GitHub ou à contacter l'équipe de développement.

---

Développé avec ❤️ par l'équipe de Gestion Intelligente d'Énergie Renouvelable
