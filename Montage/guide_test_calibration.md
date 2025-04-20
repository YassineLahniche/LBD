# Branchements du Système de Calibration pour Raspberry Pi

## 1. Branchements des pins GPIO pour les relais

| Source/Circuit | Pin GPIO (BCM) | Pin physique sur Raspberry Pi |
|----------------|---------------|------------------------------|
| Solaire        | GPIO 17       | Pin 11                       |
| Éolienne       | GPIO 27       | Pin 13                       |
| Fossile        | GPIO 22       | Pin 15                       |
| Circuit 1      | GPIO 23       | Pin 16                       |
| Circuit 2      | GPIO 24       | Pin 18                       |

## 2. Branchements I2C pour l'ADC ADS1115

| Fonction ADS1115 | Pin GPIO (BCM) | Pin physique sur Raspberry Pi |
|-----------------|---------------|------------------------------|
| SCL (Serial Clock) | GPIO 3      | Pin 5                        |
| SDA (Serial Data)  | GPIO 2      | Pin 3                        |
| VDD               | -            | Pin 2 ou 4 (5V)              |
| GND               | -            | Pin 6, 9, 14, 20, etc. (GND) |

## 3. Connexions du Convertisseur Analogique-Numérique ADS1115

| Pin ADS1115 | Connexion                        | Pin Raspberry Pi |
|------------|----------------------------------|-----------------|
| VDD        | 5V                               | Pin 2 ou 4      |
| GND        | GND                              | Pin 6, 9, 14... |
| SCL        | GPIO 3                           | Pin 5           |
| SDA        | GPIO 2                           | Pin 3           |
| A0         | Signal du capteur ACS712 Solaire | -               |
| A1         | Signal du capteur ACS712 Éolienne| -               |
| A2         | Signal du capteur ACS712 Fossile | -               |
| A3         | Signal du capteur ACS712 Sortie  | -               |

## 4. Connexions des capteurs de courant ACS712

| Pin ACS712 | Connexion                             | Destination    |
|------------|---------------------------------------|---------------|
| VCC        | 5V                                    | Raspberry Pi  |
| GND        | GND                                   | Raspberry Pi  |
| Signal     | Entrée analogique ADS1115 (A0-A3)     | ADS1115       |

| Capteur ACS712  | Canal ADS1115 | Modèle recommandé | Sensibilité |
|-----------------|--------------|------------------|-------------|
| Solaire         | A0           | ACS712 5A        | 185mV/A     |
| Éolienne        | A1           | ACS712 5A        | 185mV/A     |
| Fossile         | A2           | ACS712 30A       | 66mV/A      |
| Sortie          | A3           | ACS712 30A       | 66mV/A      |

## 5. Connexions des modules de relais

| Pin module relais | Connexion                | Destination    |
|------------------|--------------------------|---------------|
| VCC              | 5V                       | Raspberry Pi  |
| GND              | GND                      | Raspberry Pi  |
| IN               | GPIO correspondant       | Raspberry Pi  |

| Relais       | Pin GPIO | Fonction                   |
|--------------|----------|----------------------------|
| Solaire      | GPIO 17  | Contrôle source solaire    |
| Éolienne     | GPIO 27  | Contrôle source éolienne   |
| Fossile      | GPIO 22  | Contrôle source fossile    |
| Circuit 1    | GPIO 23  | Contrôle circuit sortie 1  |
| Circuit 2    | GPIO 24  | Contrôle circuit sortie 2  |

## 6. Connexions des circuits électriques aux ACS712

| Connexion Source        | ACS712                     | Connexion Destination     |
|------------------------|----------------------------|--------------------------|
| Source d'énergie (+)    | Bornier d'entrée ACS712    | Bornier de sortie ACS712  |
| Source d'énergie (-)    | Direct à destination       | Entrée système (-)        |

## 7. Connexions des circuits électriques aux relais

| Connexion Source        | Relais                     | Connexion Destination     |
|------------------------|----------------------------|--------------------------|
| Source d'alimentation (+)| Borne COM du relais        | -                         |
| -                       | Borne NO du relais         | Charge/Circuit (+)        |
| Source d'alimentation (-)| Direct à destination       | Charge/Circuit (-)        |

## Matériel nécessaire pour la calibration

| Matériel                | Quantité | Utilisation                                    |
|------------------------|----------|-----------------------------------------------|
| Multimètre             | 1        | Mesure du courant réel pour calibration        |
| Charges connues        | Min. 1   | Génération de niveaux de courant pour étalonnage |
| Fils de connexion      | Multiples| Raccordement des composants                    |
| Bornier à vis          | Selon besoin | Connexion des circuits de puissance           |
| Tournevis              | 1        | Serrage des borniers                           |

