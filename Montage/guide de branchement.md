# Guide de Branchement du Système de Gestion d'Énergie sur Raspberry Pi

## Vue d'ensemble des composants requis

- 1 Raspberry Pi (modèle 3B+ ou 4 recommandé)
- 1 convertisseur analogique-numérique ADS1115
- 3 capteurs de courant ACS712 (2 modèles 5A pour solaire/éolien, 1 modèle 30A pour fossile)
- 1 capteur de courant ACS712 supplémentaire pour mesurer le courant de sortie
- 5 modules relais (3 pour les sources d'énergie, 2 pour les circuits de distribution)
- Fils de connexion, résistances et autres composants électroniques de base
- Alimentation 5V pour le Raspberry Pi et les composants

## Correspondance des pins GPIO du Raspberry Pi

| Composant | GPIO BCM | GPIO Physique | Fonction |
|-----------|----------|---------------|----------|
| Relais Solaire | 17 | 11 | Contrôle source solaire |
| Relais Éolienne | 27 | 13 | Contrôle source éolienne |
| Relais Fossile | 22 | 15 | Contrôle source fossile |
| Relais Circuit 1 | 23 | 16 | Contrôle circuit distribution 1 |
| Relais Circuit 2 | 24 | 18 | Contrôle circuit distribution 2 |
| I2C SDA (ADS1115) | 2 | 3 | Communication I2C avec ADS1115 |
| I2C SCL (ADS1115) | 3 | 5 | Communication I2C avec ADS1115 |

## 1. Branchement de l'ADS1115

L'ADS1115 est un convertisseur analogique-numérique qui nous permet de lire les valeurs des capteurs de courant.

| ADS1115 | Raspberry Pi |
|---------|-------------|
| VDD | 3.3V (Pin 1) |
| GND | GND (Pin 6) |
| SCL | GPIO 3 / SCL (Pin 5) |
| SDA | GPIO 2 / SDA (Pin 3) |
| ADDR | GND (pour adresse par défaut 0x48) |
| ALRT | Non connecté |

## 2. Branchement des capteurs de courant ACS712

Les capteurs ACS712 convertissent le courant en une tension analogique lisible par l'ADS1115.

### Capteur de courant solaire (ACS712 5A)
| ACS712 (Solaire) | Connexion |
|------------------|-----------|
| VCC | 5V du Raspberry Pi (Pin 2 ou 4) |
| GND | GND du Raspberry Pi (Pin 6, 9, 14, 20, 25, 30, 34 ou 39) |
| OUT | A0 de l'ADS1115 |
| Bornes de courant | En série avec la ligne positive de la source solaire |

### Capteur de courant éolien (ACS712 5A)
| ACS712 (Éolien) | Connexion |
|-----------------|-----------|
| VCC | 5V du Raspberry Pi |
| GND | GND du Raspberry Pi |
| OUT | A1 de l'ADS1115 |
| Bornes de courant | En série avec la ligne positive de la source éolienne |

### Capteur de courant fossile (ACS712 30A)
| ACS712 (Fossile) | Connexion |
|------------------|-----------|
| VCC | 5V du Raspberry Pi |
| GND | GND du Raspberry Pi |
| OUT | A2 de l'ADS1115 |
| Bornes de courant | En série avec la ligne positive de la source fossile |

### Capteur de courant de sortie (ACS712)
| ACS712 (Sortie) | Connexion |
|-----------------|-----------|
| VCC | 5V du Raspberry Pi |
| GND | GND du Raspberry Pi |
| OUT | A3 de l'ADS1115 |
| Bornes de courant | En série avec la ligne de sortie après sélection des sources |

## 3. Branchement des modules relais

Les modules relais contrôlent l'activation/désactivation des sources d'énergie et la distribution entre les circuits.

### Relais source solaire
| Module Relais (Solaire) | Connexion |
|-------------------------|-----------|
| VCC | 5V du Raspberry Pi |
| GND | GND du Raspberry Pi |
| IN | GPIO 17 (Pin 11) du Raspberry Pi |
| Contacts NO/COM/NC | Connectés pour commuter la source solaire |

### Relais source éolienne
| Module Relais (Éolien) | Connexion |
|------------------------|-----------|
| VCC | 5V du Raspberry Pi |
| GND | GND du Raspberry Pi |
| IN | GPIO 27 (Pin 13) du Raspberry Pi |
| Contacts NO/COM/NC | Connectés pour commuter la source éolienne |

### Relais source fossile
| Module Relais (Fossile) | Connexion |
|-------------------------|-----------|
| VCC | 5V du Raspberry Pi |
| GND | GND du Raspberry Pi |
| IN | GPIO 22 (Pin 15) du Raspberry Pi |
| Contacts NO/COM/NC | Connectés pour commuter la source fossile |

### Relais circuit 1
| Module Relais (Circuit 1) | Connexion |
|---------------------------|-----------|
| VCC | 5V du Raspberry Pi |
| GND | GND du Raspberry Pi |
| IN | GPIO 23 (Pin 16) du Raspberry Pi |
| Contacts NO/COM/NC | Connectés pour activer/désactiver le circuit 1 |

### Relais circuit 2
| Module Relais (Circuit 2) | Connexion |
|---------------------------|-----------|
| VCC | 5V du Raspberry Pi |
| GND | GND du Raspberry Pi |
| IN | GPIO 24 (Pin 18) du Raspberry Pi |
| Contacts NO/COM/NC | Connectés pour activer/désactiver le circuit 2 |

## 4. Schéma de connexion du système d'alimentation

Le système complet utilise 3 sources d'alimentation qui sont commutées par les relais vers 2 circuits de distribution.

```
Sources d'énergie:
┌───────────┐     ┌───────────┐     ┌───────────┐
│  Solaire  │     │  Éolienne │     │  Fossile  │
└────┬──────┘     └────┬──────┘     └────┬──────┘
     │                 │                 │
     ▼                 ▼                 ▼
┌────┴──────┐     ┌────┴──────┐     ┌────┴──────┐
│  Capteur  │     │  Capteur  │     │  Capteur  │
│  ACS712   │     │  ACS712   │     │  ACS712   │
│  (A0)     │     │  (A1)     │     │  (A2)     │
└────┬──────┘     └────┬──────┘     └────┬──────┘
     │                 │                 │
     ▼                 ▼                 ▼
┌────┴──────┐     ┌────┴──────┐     ┌────┴──────┐
│   Relais  │     │   Relais  │     │   Relais  │
│  (GPIO 17)│     │  (GPIO 27)│     │  (GPIO 22)│
└────┬──────┘     └────┬──────┘     └────┬──────┘
     │                 │                 │
     └─────────────────┼─────────────────┘
                       │
                       ▼
                 ┌─────┴─────┐
                 │  Capteur  │
                 │  ACS712   │
                 │   (A3)    │
                 └─────┬─────┘
                       │
                       ▼
          ┌────────────┴───────────┐
          │                        │
     ┌────▼─────┐            ┌─────▼────┐
     │  Relais  │            │  Relais  │
     │ Circuit 1│            │ Circuit 2│
     │(GPIO 23) │            │(GPIO 24) │
     └────┬─────┘            └─────┬────┘
          │                        │
          ▼                        ▼
     ┌────┴─────┐            ┌─────┴────┐
     │Circuit de│            │Circuit de│
     │ charge 1 │            │ charge 2 │
     └──────────┘            └──────────┘
```

## 5. Notes importantes sur les branchements

1. **Alimentation des relais**
   - Si vous utilisez des modules relais qui requièrent 5V pour s'activer (active-low), assurez-vous de les connecter comme indiqué ci-dessus
   - Si vos relais sont active-high, inversez la logique dans le code

2. **Protection du Raspberry Pi**
   - Utilisez des diodes de protection 1N4001/1N4007 en parallèle avec les bobines des relais pour protéger contre les tensions inverses
   - Considérez l'ajout de résistances pull-down (10kΩ) sur les entrées des relais

3. **Calibration des capteurs ACS712**
   - Les capteurs ACS712 peuvent nécessiter une calibration pour des mesures précises
   - Mesurez la tension de sortie à courant zéro pour déterminer l'offset exact
   - Utilisez un multimètre pour vérifier et ajuster les valeurs ACS712_OFFSET dans le code

4. **Sources d'alimentation**
   - Utilisez une alimentation 5V séparée et stable pour le Raspberry Pi
   - Assurez-vous que l'alimentation peut fournir suffisamment de courant pour tous les relais (min. 2A recommandé)

5. **Sécurité électrique**
   - Pour les sources à tension élevée (solaire, éolienne), utilisez des isolateurs optiques ou des relais appropriés
   - Ne manipulez jamais les connexions lorsque le système est sous tension
   - Installez des fusibles appropriés sur chaque ligne d'alimentation

## 6. Verification des branchements

Avant de démarrer le script Python, vérifiez:

1. Que l'ADS1115 est bien détecté avec la commande: `i2cdetect -y 1`
2. Que les tensions de référence des capteurs ACS712 sont correctes (environ 2.5V à courant zéro)
3. Que les relais s'activent correctement avec des tests GPIO simples:
   ```
   gpio -g mode 17 out
   gpio -g write 17 1  # Activer
   gpio -g write 17 0  # Désactiver
   ```

## 7. Mise à jour des paramètres dans le code

Après installation, vous devrez peut-être ajuster les valeurs suivantes dans le code selon vos mesures:

```python
ACS712_OFFSET = {
    'solaire': 2.5,  # Ajustez selon la tension mesurée à 0A
    'eolienne': 2.5, # Ajustez selon la tension mesurée à 0A
    'fossile': 2.5   # Ajustez selon la tension mesurée à 0A
}

SOURCE_CURRENT_THRESHOLDS = {
    'solaire': 0.5,  # Ajustez selon vos besoins
    'eolienne': 0.3, # Ajustez selon vos besoins
    'fossile': 1.0   # Ajustez selon vos besoins
}
```