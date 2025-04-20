# Guide de Sécurité pour le Système de Gestion d'Énergie Intelligent

Je vais vous présenter les règles de sécurité essentielles et les vérifications techniques spécifiques pour votre projet de gestion d'énergie intelligent. Ces instructions sont particulièrement destinées aux débutants en électronique.

## 1. Règles de Sécurité Générales

### Électricité et Manipulation
- **Toujours couper l'alimentation** avant tout branchement ou modification du circuit
- **Porter des gants isolants** lorsque vous travaillez avec des tensions supérieures à 24V
- **Utiliser des outils isolés** (tournevis à manche isolant) pour le travail électrique
- **Ne jamais travailler seul** sur des circuits à tension dangereuse
- **Avoir un extincteur de classe C** à proximité (pour les feux électriques)

### Espace de Travail
- Travailler dans un environnement **sec et bien éclairé**
- Utiliser un **tapis antistatique** pour protéger les composants électroniques
- Maintenir la **zone de travail dégagée** et organisée
- **Étiqueter clairement** tous les câbles et composants

## 2. Vérifications Techniques par Composant

### Raspberry Pi
**Sécurité et Vérifications:**
- Utilisez une **alimentation 5V officielle** ou de qualité certifiée (minimum 2.5A)
- **Inspectez visuellement** le Raspberry Pi avant chaque utilisation (absence de dommages ou déformations)
- Vérifiez que le **circuit électrique** utilisé dispose d'une protection contre les surcharges
- **Mesurez la tension de sortie** de l'alimentation avec un multimètre avant connexion
- **N'insérez jamais d'objets métalliques** dans les connecteurs du Raspberry Pi

**Procédure de Test:**
1. Branchez uniquement l'alimentation et vérifiez que le voyant d'alimentation s'allume
2. Connectez un écran HDMI pour vérifier que le système démarre correctement
3. Exécutez `vcgencmd measure_temp` pour vérifier la température de fonctionnement
4. Assurez-vous que le système I2C est activé avec `sudo raspi-config`

### Convertisseur Analogique-Numérique ADS1115
**Sécurité et Vérifications:**
- Ne jamais connecter des tensions supérieures à 5V sur les entrées
- Vérifier les **soudures des broches** avant utilisation
- S'assurer que l'alimentation est stable et filtrée
- Utiliser des **résistances de pull-up** sur les lignes I2C (typiquement 4.7kΩ)

**Procédure de Test:**
1. Connectez VDD à 3.3V, GND à GND, SDA et SCL aux pins correspondants
2. Exécutez `i2cdetect -y 1` pour vérifier que le périphérique est reconnu (adresse 0x48 par défaut)
3. Mesurez la tension entre VDD et GND (doit être proche de 3.3V)
4. Vérifiez la continuité entre les broches du Raspberry Pi et de l'ADS1115

### Capteurs de Courant ACS712
**Sécurité et Vérifications:**
- **Isoler électriquement** le capteur des circuits à haute tension
- Vérifier l'**absence de traces de surchauffe** (décoloration)
- Mesurer la **résistance entre VCC et GND** (ne doit pas être en court-circuit)
- Utiliser des **fusibles appropriés** en amont du capteur:
  - Pour modèle 5A: fusible de 5A maximum
  - Pour modèle 30A: fusible de 20A maximum

**Procédure de Test:**
1. Alimentez le capteur en 5V sans connecter de charge
2. Mesurez la tension de sortie à vide (devrait être environ 2.5V)
3. Exécutez le script de calibration avec `python3 test_calibration.py` pour vérifier le point zéro
4. Utilisez une charge connue (ex: ampoule 12V) avec un multimètre en série pour calibrer

### Modules Relais
**Sécurité et Vérifications:**
- **Vérifier le mode de fonctionnement** (active-low ou active-high)
- **Installer des diodes de protection** (1N4007) en parallèle avec les bobines
- Ne jamais dépasser le **courant nominal des contacts** (généralement 10A)
- Utiliser des **fusibles appropriés** pour chaque circuit contrôlé
- **Inspecter les soudures** et connexions avant chaque utilisation

**Procédure de Test:**
1. Vérifiez la résistance entre la bobine (typiquement 70-120Ω pour un relais 5V)
2. Connectez uniquement l'alimentation 5V et GND
3. Testez chaque relais individuellement avec le script `test_calibration.py` option 1
4. Écoutez le "clic" caractéristique du relais lors de la commutation
5. Vérifiez la continuité des contacts avec un multimètre en mode test de continuité

### Câblage
**Sécurité et Vérifications:**
- Utiliser des **fils de section adaptée** au courant prévu:
  - Pour les signaux de commande: 22-26 AWG
  - Pour les circuits de puissance jusqu'à 5A: 18-20 AWG
  - Pour les circuits de puissance jusqu'à 10A: 16 AWG
  - Pour les circuits de puissance supérieurs à 10A: 14 AWG ou plus
- **Vérifier l'isolation** des fils et câbles
- **Éviter les boucles de courant** dans le câblage
- **Utiliser des connecteurs sertis** plutôt que des fils nus torsadés

**Procédure de Test:**
1. Testez chaque connexion avec un multimètre en mode continuité
2. Vérifiez qu'il n'y a pas de court-circuit entre les fils adjacents
3. Tirez doucement sur chaque fil pour vérifier la solidité des connexions
4. Utilisez des serre-câbles ou des gaines thermorétractables pour sécuriser les connexions

## 3. Vérifications Spécifiques pour Chaque Source d'Énergie

### Source Solaire
**Sécurité et Vérifications:**
- Installer un **régulateur de charge solaire** entre les panneaux et le système
- Ajouter des **diodes de blocage** pour éviter les courants inverses
- Vérifier que la **tension du panneau** est compatible avec votre système
- Utiliser des **fusibles DC spécifiques** pour les installations solaires

**Procédure de Test:**
1. Mesurez la tension en circuit ouvert des panneaux solaires
2. Vérifiez la polarité des connexions
3. Testez le circuit complet avec une charge légère avant de connecter au système principal
4. Calibrez le capteur ACS712 spécifiquement pour cette source

### Source Éolienne
**Sécurité et Vérifications:**
- Installer un **circuit de freinage** d'urgence pour l'éolienne
- Utiliser un **régulateur de charge éolien** avec protection contre les surtensions
- Vérifier la **mise à la terre** du mât de l'éolienne
- Protéger le circuit contre les **surtensions induites par la foudre**

**Procédure de Test:**
1. Testez d'abord la sortie de l'éolienne avec un multimètre
2. Connectez progressivement la charge en surveillant la tension et le courant
3. Vérifiez que le système peut gérer les variations rapides de tension
4. Calibrez le capteur ACS712 avec différentes vitesses de vent si possible

### Source Fossile (Générateur)
**Sécurité et Vérifications:**
- Installer une **protection contre les retours de courant**
- Vérifier la **mise à la terre** du générateur
- Installer un **filtre anti-parasites** pour protéger l'électronique sensible
- Utiliser un **contrôleur de groupe électrogène** avec démarrage/arrêt automatique

**Procédure de Test:**
1. Démarrez le générateur sans charge et vérifiez la tension et la fréquence
2. Augmentez progressivement la charge en surveillant les paramètres
3. Vérifiez que le système de commutation fonctionne correctement
4. Calibrez le capteur ACS712 avec différentes charges appliquées

## 4. Mise en Service et Tests Finaux

### Tests d'Intégration
1. **Tester chaque composant individuellement** avant l'assemblage complet
2. Effectuer un **test de calibration** complet avec `python3 test_calibration.py`
3. Vérifier le **système de priorisation des sources** avec différentes combinaisons
4. Tester la **commutation des circuits** selon les seuils définis
5. Effectuer un **test de charge maximale** pour chaque circuit
6. Mesurer la **consommation du système** au repos et en fonctionnement

### Vérifications de Sécurité Finales
1. Vérifier que tous les **conducteurs sont isolés** et protégés
2. Tester les **protections contre les surintensités** (fusibles)
3. Vérifier que les **alarmes et surveillances** fonctionnent correctement
4. S'assurer que l'**arrêt d'urgence** est facilement accessible
5. Contrôler la **température des composants** après une heure de fonctionnement

## 5. Documentation et Maintenance

1. **Documenter toutes les valeurs de calibration** dans un journal
2. **Créer un schéma de câblage** complet et précis
3. **Établir un calendrier de maintenance préventive**:
   - Vérification mensuelle des connexions électriques
   - Test des relais tous les 3 mois
   - Recalibration des capteurs tous les 6 mois
4. **Conserver une copie de sauvegarde** des scripts et paramètres de configuration
5. **Étiqueter clairement** tous les fusibles et disjoncteurs avec leurs valeurs nominales

En suivant ces consignes de sécurité et procédures de vérification, vous pourrez installer et maintenir votre système de gestion d'énergie intelligent en toute sécurité, même si vous êtes débutant en électronique.