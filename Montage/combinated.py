#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SYSTÈME DE GESTION D'ÉNERGIE INTELLIGENT INTÉGRÉ
================================================

Ce script combine deux sous-systèmes :
1. Gestionnaire de Sources : Sélectionne entre sources solaire, éolienne et fossile selon priorité
2. Contrôleur de Distribution : Distribue l'énergie entre deux circuits selon charge

Architecture du système :
- Les capteurs mesurent le courant disponible de chaque source d'énergie
- L'algorithme de priorisation sélectionne la/les source(s) optimale(s)
- Le courant résultant est mesuré et dirigé vers l'un des deux circuits finaux
  selon un mécanisme d'hystérésis basé sur les seuils de courant

Auteur : [Votre nom]
Date : 20 avril 2025
"""

import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import logging
import threading

# =====================================================================
# CONFIGURATION DU LOGGING
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("energy_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =====================================================================
# CONSTANTES ET PARAMÈTRES DU SYSTÈME
# =====================================================================

# Paramètres pour le gestionnaire de sources d'énergie
SOURCE_RELAY_PINS = {
    'solaire': 17,   # GPIO 17 pour la source solaire
    'eolienne': 27,  # GPIO 27 pour la source éolienne
    'fossile': 22    # GPIO 22 pour la source fossile
}

SOURCE_CURRENT_THRESHOLDS = {
    'solaire': 0.5,  # 0.5A minimum pour le solaire
    'eolienne': 0.3, # 0.3A minimum pour l'éolien
    'fossile': 1.0   # 1.0A minimum pour la source fossile
}

ACS712_FACTORS = {
    'solaire': 0.185,  # 185mV par ampère pour ACS712 5A
    'eolienne': 0.185, # 185mV par ampère pour ACS712 5A 
    'fossile': 0.066   # 66mV par ampère pour ACS712 30A
}

ACS712_OFFSET = {
    'solaire': 2.5,  # Tension de référence à 0A
    'eolienne': 2.5, # Tension de référence à 0A
    'fossile': 2.5   # Tension de référence à 0A
}

# Paramètres pour le contrôleur de distribution
DISTRIBUTION_RELAY_PINS = {
    'circuit1': 23,  # GPIO 23 pour le circuit 1
    'circuit2': 24   # GPIO 24 pour le circuit 2
}

# Paramètres de seuils et d'hystérésis
CURRENT_HIGH_THRESHOLD = 2.0   # Ampères - seuil pour basculer vers circuit 1
CURRENT_LOW_THRESHOLD = 1.5    # Ampères - seuil pour basculer vers circuit 2
HYSTERESIS = 0.2               # Valeur d'hystérésis pour éviter les oscillations
SAMPLING_DELAY = 0.5           # Secondes entre chaque lecture

# =====================================================================
# CLASSE GESTIONNAIRE DE SOURCES D'ÉNERGIE
# =====================================================================

class EnergySourceManager:
    """
    Système de gestion qui priorise et sélectionne entre trois sources d'énergie
    (solaire, éolienne, fossile) selon leur disponibilité et un ordre de priorité.
    """
    
    def __init__(self, adc):
        """
        Initialise le gestionnaire de sources d'énergie
        
        Args:
            adc: Instance de l'ADC ADS1115 déjà configurée
        """
        # Configuration GPIO pour les relais des sources
        for pin in SOURCE_RELAY_PINS.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # Relais désactivés par défaut (HIGH = OFF pour relais NC)
        
        # Configuration des canaux pour les capteurs de courant
        self.current_sensors = {
            'solaire': AnalogIn(adc, ADS.P0),    # Canal A0
            'eolienne': AnalogIn(adc, ADS.P1),   # Canal A1
            'fossile': AnalogIn(adc, ADS.P2)     # Canal A2
        }
        
        # Variables d'état
        self.active_sources = {source: False for source in SOURCE_RELAY_PINS.keys()}
        self.current_readings = {source: 0.0 for source in SOURCE_RELAY_PINS.keys()}
        self.output_current = 0.0  # Courant total en sortie
        
        logger.info("Gestionnaire de sources d'énergie initialisé")
    
    def read_current(self, source):
        """
        Lit le courant d'une source donnée via son capteur
        
        Args:
            source: Nom de la source ('solaire', 'eolienne', 'fossile')
            
        Returns:
            float: Courant en ampères
        """
        try:
            voltage = self.current_sensors[source].voltage
            current = (voltage - ACS712_OFFSET[source]) / ACS712_FACTORS[source]
            
            # Éliminer les lectures négatives (bruit)
            if current < 0:
                current = 0
            
            self.current_readings[source] = current
            return current
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du capteur {source}: {e}")
            return 0.0
    
    def toggle_source(self, source, state=True):
        """
        Active ou désactive une source d'énergie
        
        Args:
            source: Nom de la source à contrôler
            state: True pour activer, False pour désactiver
        """
        try:
            # Inverser l'état car les relais sont normalement fermés (LOW = ON, HIGH = OFF)
            GPIO.output(SOURCE_RELAY_PINS[source], not state)
            self.active_sources[source] = state
            if state:
                logger.info(f"Source {source} activée")
            else:
                logger.info(f"Source {source} désactivée")
        except Exception as e:
            logger.error(f"Erreur lors de la commande du relais {source}: {e}")
    
    def select_sources(self):
        """
        Algorithme de sélection des sources basé sur la priorité:
        solaire > éolienne > fossile
        
        Returns:
            float: Courant total estimé en sortie après sélection des sources
        """
        # Lire les courants de toutes les sources
        solar_current = self.read_current('solaire')
        wind_current = self.read_current('eolienne')
        fossil_current = self.read_current('fossile')
        
        logger.info(f"Lectures des courants - Solaire: {solar_current:.2f}A, Éolien: {wind_current:.2f}A, Fossile: {fossil_current:.2f}A")
        
        # Déterminer quelles sources sont disponibles
        solar_available = solar_current >= SOURCE_CURRENT_THRESHOLDS['solaire']
        wind_available = wind_current >= SOURCE_CURRENT_THRESHOLDS['eolienne']
        fossil_available = fossil_current >= SOURCE_CURRENT_THRESHOLDS['fossile']
        
        # Désactiver toutes les sources par défaut
        for source in self.active_sources:
            self.toggle_source(source, False)
        
        # Réinitialiser le courant total de sortie
        self.output_current = 0.0
        
        # Appliquer la logique de priorisation
        if solar_available and wind_available:
            # Combiner solaire et éolien si les deux sont disponibles
            logger.info("Combinaison des sources solaire et éolienne")
            self.toggle_source('solaire', True)
            self.toggle_source('eolienne', True)
            self.output_current = solar_current + wind_current
        elif solar_available:
            # Utiliser solaire uniquement
            logger.info("Utilisation de la source solaire uniquement")
            self.toggle_source('solaire', True)
            self.output_current = solar_current
        elif wind_available:
            # Utiliser éolien uniquement
            logger.info("Utilisation de la source éolienne uniquement")
            self.toggle_source('eolienne', True)
            self.output_current = wind_current
        elif fossil_available:
            # Utiliser fossile en dernier recours
            logger.info("Utilisation de la source fossile (dernier recours)")
            self.toggle_source('fossile', True)
            self.output_current = fossil_current
        else:
            # Aucune source disponible
            logger.warning("Aucune source d'énergie disponible, système en attente")
            self.output_current = 0.0
        
        return self.output_current


# =====================================================================
# CLASSE CONTRÔLEUR DE DISTRIBUTION
# =====================================================================

class DistributionController:
    """
    Système de distribution qui dirige le courant vers l'un des deux circuits
    selon un mécanisme d'hystérésis basé sur les seuils de courant.
    """
    
    def __init__(self, adc):
        """
        Initialise le contrôleur de distribution
        
        Args:
            adc: Instance de l'ADC ADS1115 déjà configurée
        """
        # Configuration GPIO pour les relais de distribution
        for pin in DISTRIBUTION_RELAY_PINS.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)  # Désactiver les deux relais au démarrage
        
        # Configuration du capteur de courant de sortie
        self.output_sensor = AnalogIn(adc, ADS.P3)  # Canal A3 pour mesurer le courant effectif en sortie
        
        # Variables d'état
        self.circuit1_active = False
        self.circuit2_active = False
        
        logger.info("Contrôleur de distribution initialisé")
    
    def read_output_current(self):
        """
        Lit le courant effectif en sortie du système
        
        Returns:
            float: Courant en ampères
        """
        try:
            voltage = self.output_sensor.voltage
            # Ajuster selon votre capteur spécifique
            current = (voltage - 2.5) / 0.066  # Exemple pour un ACS712 30A
            
            # Éliminer les lectures négatives (bruit)
            if current < 0:
                current = 0
            
            return current
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du capteur de sortie: {e}")
            return 0.0
    
    def activate_circuit1(self):
        """Active le circuit 1 et désactive le circuit 2"""
        if not self.circuit1_active:
            logger.info("Activation du circuit 1")
            # Désactiver circuit 2 d'abord pour éviter toute activation simultanée
            GPIO.output(DISTRIBUTION_RELAY_PINS['circuit2'], GPIO.LOW)
            time.sleep(0.1)  # Petit délai de sécurité
            GPIO.output(DISTRIBUTION_RELAY_PINS['circuit1'], GPIO.HIGH)
            self.circuit1_active = True
            self.circuit2_active = False
    
    def activate_circuit2(self):
        """Active le circuit 2 et désactive le circuit 1"""
        if not self.circuit2_active:
            logger.info("Activation du circuit 2")
            # Désactiver circuit 1 d'abord pour éviter toute activation simultanée
            GPIO.output(DISTRIBUTION_RELAY_PINS['circuit1'], GPIO.LOW)
            time.sleep(0.1)  # Petit délai de sécurité
            GPIO.output(DISTRIBUTION_RELAY_PINS['circuit2'], GPIO.HIGH)
            self.circuit2_active = True
            self.circuit1_active = False
    
    def distribute_power(self, input_current):
        """
        Distribue l'énergie entre les circuits selon le courant d'entrée
        
        Args:
            input_current: Courant estimé en entrée (venant du gestionnaire de sources)
        """
        # Mesurer le courant effectif en sortie pour confirmation
        actual_current = self.read_output_current()
        logger.info(f"Courant estimé: {input_current:.2f}A, Courant mesuré en sortie: {actual_current:.2f}A")
        
        # Logique de contrôle avec hystérésis
        if input_current > (CURRENT_HIGH_THRESHOLD + HYSTERESIS) or \
           (input_current > (CURRENT_HIGH_THRESHOLD - HYSTERESIS) and self.circuit1_active):
            self.activate_circuit1()
        elif input_current < (CURRENT_LOW_THRESHOLD - HYSTERESIS) or \
             (input_current < (CURRENT_LOW_THRESHOLD + HYSTERESIS) and self.circuit2_active):
            self.activate_circuit2()
        
        # Pour des fins de diagnostic, lire à nouveau après commutation
        if self.circuit1_active or self.circuit2_active:
            time.sleep(0.2)  # Petit délai pour stabilisation
            after_current = self.read_output_current()
            active_circuit = "circuit1" if self.circuit1_active else "circuit2"
            logger.info(f"Circuit actif: {active_circuit}, Courant après commutation: {after_current:.2f}A")


# =====================================================================
# CLASSE PRINCIPALE: SYSTÈME DE GESTION D'ÉNERGIE INTÉGRÉ
# =====================================================================

class IntegratedEnergySystem:
    """
    Système intégré qui combine le gestionnaire de sources et le contrôleur
    de distribution pour une gestion complète de l'énergie.
    """
    
    def __init__(self):
        """Initialise le système de gestion d'énergie intégré"""
        # Configuration initiale
        GPIO.setmode(GPIO.BCM)
        
        # Initialisation de l'ADC ADS1115
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        
        # Créer les sous-systèmes
        self.source_manager = EnergySourceManager(self.ads)
        self.distribution_controller = DistributionController(self.ads)
        
        self.running = False
        logger.info("Système de gestion d'énergie intégré initialisé")
    
    def execute_control_loop(self):
        """Boucle principale de contrôle exécutée en continu"""
        logger.info("Démarrage de la boucle de contrôle")
        
        try:
            while self.running:
                # Étape 1: Sélectionner les sources optimales
                output_current = self.source_manager.select_sources()
                
                # Étape 2: Distribuer l'énergie selon le courant disponible
                self.distribution_controller.distribute_power(output_current)
                
                # Attendre avant la prochaine itération
                time.sleep(SAMPLING_DELAY)
        except Exception as e:
            logger.error(f"Erreur dans la boucle de contrôle: {e}")
        finally:
            # Nettoyage en cas d'arrêt
            self.stop()
    
    def start(self):
        """Démarre le système de gestion d'énergie"""
        if not self.running:
            self.running = True
            # Lancer la boucle de contrôle dans un thread séparé
            self.control_thread = threading.Thread(target=self.execute_control_loop)
            self.control_thread.daemon = True
            self.control_thread.start()
            logger.info("Système de gestion d'énergie démarré")
            return True
        return False
    
    def stop(self):
        """Arrête le système de gestion d'énergie en toute sécurité"""
        self.running = False
        
        # Désactiver tous les relais des sources
        for source in self.source_manager.active_sources:
            self.source_manager.toggle_source(source, False)
        
        # Désactiver les relais de distribution
        GPIO.output(DISTRIBUTION_RELAY_PINS['circuit1'], GPIO.LOW)
        GPIO.output(DISTRIBUTION_RELAY_PINS['circuit2'], GPIO.LOW)
        
        logger.info("Système de gestion d'énergie arrêté")
    
    def cleanup(self):
        """Nettoie les ressources GPIO utilisées"""
        GPIO.cleanup()
        logger.info("Ressources GPIO libérées")


# =====================================================================
# FONCTION PRINCIPALE
# =====================================================================

def main():
    """Point d'entrée principal du programme"""
    try:
        # Afficher un message de démarrage
        print("=================================================================")
        print("  SYSTÈME DE GESTION D'ÉNERGIE INTELLIGENT INTÉGRÉ")
        print("  Version 1.0")
        print("=================================================================")
        print("Démarrage du système...")
        
        # Créer une instance du système intégré
        system = IntegratedEnergySystem()
        
        # Démarrer le système
        system.start()
        
        # Maintenir le programme en vie jusqu'à interruption
        print("Système en cours d'exécution. Appuyez sur Ctrl+C pour arrêter.")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur")
        logger.info("Programme interrompu par l'utilisateur")
    except Exception as e:
        print(f"\nErreur critique: {e}")
        logger.error(f"Erreur critique: {e}")
    finally:
        if 'system' in locals():
            print("Arrêt du système...")
            system.stop()
            system.cleanup()
            print("Système arrêté en toute sécurité")


if __name__ == "__main__":
    main()