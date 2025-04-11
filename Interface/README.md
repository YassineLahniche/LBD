# Système de Gestion Intelligente d'Énergie Renouvelable

Ce projet vise à optimiser l'utilisation des sources d'énergies renouvelables (solaire, éolien) en temps réel, en utilisant un agent d'apprentissage par renforcement (RL) pour prendre des décisions optimales d'allocation d'énergie.

## Structure du projet

```
.
├── assets/
│   └── icons/
│       ├── grid.svg
│       ├── icon1.png
│       ├── icon2.png
│       ├── solar.svg
│       └── wind.svg
├── scripts/
│   ├── api.js
│   ├── app.js
│   ├── forecast.js
│   ├── energy-graph.js
│   └── ui.js
├── style/
│   └── main.css
├── api.py
├── weather_api.py
├── energy-graph.html
├── forecast.html
├── index.html
└── README.md
```

## Fonctionnalités

- **Suivi en temps réel** des puissances mesurées des sources d'énergie (solaire, éolien, réseau)
- **Prise de décision optimale** par un agent d'apprentissage par renforcement
- **Visualisation de données météorologiques** pour prévoir la production d'énergie
- **Interface dynamique** affichant la génération et l'allocation d'énergie
- **Historique et graphiques** pour analyser les performances

## Installation et configuration

1. Cloner le dépôt
2. Installer les dépendances Python:
   ```
   pip install flask flask-cors requests
   ```
3. Lancer le serveur API:
   ```
   python api.py
   ```
4. Ouvrir index.html dans votre navigateur

## API Météorologique

Le projet utilise l'API Open-Meteo pour récupérer les données météorologiques:
- Température
- Vitesse du vent
- Rayonnement solaire
- Pression atmosphérique

Ces données sont utilisées pour:
1. Calculer la production potentielle d'énergie solaire
2. Calculer la production potentielle d'énergie éolienne
3. Guider l'agent RL dans ses décisions d'allocation

## Capteurs et Matériel

- Raspberry Pi pour collecter les données
- Capteurs de courant pour mesurer la production des sources d'énergie
- Configuration à adapter selon votre installation

## Personnalisation

Les paramètres des sources d'énergie sont configurables:
- Rayon des turbines éoliennes (`TURBINE_RADIUS`)
- Efficacité des turbines (`EFFICIENCY_WIND`)
- Efficacité des panneaux solaires (`EFFICIENCY_SOLAR`)

## Agent d'apprentissage par renforcement

L'agent RL est conçu pour optimiser l'allocation d'énergie en fonction:
- Des conditions météorologiques actuelles et prévues
- De la charge requise
- Des coûts d'utilisation des différentes sources

## Contribution

Les contributions sont les bienvenues! N'hésitez pas à soumettre des pull requests ou à signaler des bugs.

## Licence

Ce projet est sous licence MIT.