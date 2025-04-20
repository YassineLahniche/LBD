#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Système de Gestion Intelligente d'Énergie
-----------------------------------------
Ce script implémente un système de gestion d'énergie pour Raspberry Pi
qui contrôle trois sources d'énergie (solaire, éolienne, fossile) via des capteurs
de courant et des relais, selon un algorithme de priorisation.
"""

import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import logging
import threading

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("energy_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnergyManagementSystem:
    """Système de gestion intelligente d'énergie pour Raspberry Pi"""
    
    # Définition des pins GPIO pour les relais
    RELAY_PINS = {
        'solaire': 17,   # GPIO 17 pour le relais de la source solaire
        'eolienne': 27,  # GPIO 27 pour le relais de la source éolienne
        'fossile': 22,   # GPIO 22 pour le relais de la source fossile
        'pompe': 23      # GPIO 23 pour le relais de la pompe
    }
    
    # Seuils de courant (en ampères) pour considérer une source comme disponible
    COURANT_SEUILS = {
        'solaire': 0.5,    # 0.5A minimum pour le solaire
        'eolienne': 0.3,   # 0.3A minimum pour l'éolien
        'fossile': 1.0     # 1.0A minimum pour la source fossile
    }
    
    # Facteurs de conversion pour les capteurs de courant ACS712
    # Ces valeurs doivent être ajustées selon vos capteurs spécifiques
    ACS712_FACTEURS = {
        'solaire': 0.185,   # 185mV par ampère pour ACS712 5A
        'eolienne': 0.185,  # 185mV par ampère pour ACS712 5A
        'fossile': 0.066    # 66mV par ampère pour ACS712 30A
    }
    
    # Offset des capteurs (en volts)
    ACS712_OFFSET = {
        'solaire': 2.5,    # Tension de référence à 0A
        'eolienne': 2.5,   # Tension de référence à 0A
        'fossile': 2.5     # Tension de référence à 0A
    }
    
    def __init__(self):
        """Initialise le système de gestion d'énergie"""
        # Configuration du GPIO
        GPIO.setmode(GPIO.BCM)
        for pin in self.RELAY_PINS.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # Relais désactivés par défaut (HIGH = OFF pour les relais normalement fermés)
        
        # Initialisation de l'ADC ADS1115
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(i2c)
        
        # Configuration des canaux ADC pour les capteurs de courant
        self.capteurs = {
            'solaire': AnalogIn(self.ads, ADS.P0),   # Canal A0
            'eolienne': AnalogIn(self.ads, ADS.P1),  # Canal A1
            'fossile': AnalogIn(self.ads, ADS.P2)    # Canal A2
        }
        
        self.running = False
        self.sources_actives = {source: False for source in ['solaire', 'eolienne', 'fossile']}
        self.courants = {source: 0.0 for source in ['solaire', 'eolienne', 'fossile']}
        self.pompe_active = False
        
        logger.info("Système de gestion d'énergie initialisé")
    
    def lire_courant(self, source):
        """
        Lit le courant d'une source donnée via son capteur.
        Convertit la tension du capteur en ampères selon les spécifications du ACS712.
        """
        try:
            tension = self.capteurs[source].voltage
            courant = (tension - self.ACS712_OFFSET[source]) / self.ACS712_FACTEURS[source]
            
            # Éliminer les lectures négatives (bruit)
            if courant < 0:
                courant = 0
            
            self.courants[source] = courant
            return courant
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du capteur {source}: {e}")
            return 0.0
    
    def activer_relais(self, source, etat=True):
        """Active ou désactive un relais pour une source donnée"""
        try:
            # Inverser l'état car les relais sont normalement fermés (LOW = ON, HIGH = OFF)
            GPIO.output(self.RELAY_PINS[source], not etat)
            self.sources_actives[source] = etat
            if etat:
                logger.info(f"Source {source} activée")
            else:
                logger.info(f"Source {source} désactivée")
        except Exception as e:
            logger.error(f"Erreur lors de la commande du relais {source}: {e}")
    
    def activer_pompe(self, etat=True):
        """Active ou désactive la pompe"""
        try:
            GPIO.output(self.RELAY_PINS['pompe'], not etat)  # Inverser pour les relais normalement fermés
            self.pompe_active = etat
            if etat:
                logger.info("Pompe activée")
            else:
                logger.info("Pompe désactivée")
        except Exception as e:
            logger.error(f"Erreur lors de la commande de la pompe: {e}")
    
    def prendre_decision(self):
        """
        Algorithme de prise de décision basé sur la disponibilité des sources
        et l'ordre de priorité: solaire > éolienne > fossile
        """
        # Lire les courants de toutes les sources
        courant_solaire = self.lire_courant('solaire')
        courant_eolien = self.lire_courant('eolienne')
        courant_fossile = self.lire_courant('fossile')
        
        logger.info(f"Lectures des courants - Solaire: {courant_solaire:.2f}A, Éolien: {courant_eolien:.2f}A, Fossile: {courant_fossile:.2f}A")
        
        # Déterminer quelles sources sont disponibles
        solaire_disponible = courant_solaire >= self.COURANT_SEUILS['solaire']
        eolien_disponible = courant_eolien >= self.COURANT_SEUILS['eolienne']
        fossile_disponible = courant_fossile >= self.COURANT_SEUILS['fossile']
        
        # Désactiver toutes les sources par défaut
        for source in self.sources_actives:
            self.activer_relais(source, False)
        
        # Appliquer la logique de priorisation
        if solaire_disponible and eolien_disponible:
            # Combiner solaire et éolien si les deux sont disponibles
            logger.info("Combinaison des sources solaire et éolienne")
            self.activer_relais('solaire', True)
            self.activer_relais('eolienne', True)
            self.activer_pompe(True)
        elif solaire_disponible:
            # Utiliser solaire uniquement
            logger.info("Utilisation de la source solaire uniquement")
            self.activer_relais('solaire', True)
            self.activer_pompe(True)
        elif eolien_disponible:
            # Utiliser éolien uniquement
            logger.info("Utilisation de la source éolienne uniquement")
            self.activer_relais('eolienne', True)
            self.activer_pompe(True)
        elif fossile_disponible:
            # Utiliser fossile en dernier recours
            logger.info("Utilisation de la source fossile (dernier recours)")
            self.activer_relais('fossile', True)
            self.activer_pompe(True)
        else:
            # Aucune source disponible
            logger.warning("Aucune source d'énergie disponible, système en attente")
            self.activer_pompe(False)
    
    def executer_boucle_controle(self):
        """Boucle principale de contrôle exécutée en continu"""
        logger.info("Démarrage de la boucle de contrôle")
        
        try:
            while self.running:
                self.prendre_decision()
                time.sleep(5)  # Attendre 5 secondes avant la prochaine itération
        except Exception as e:
            logger.error(f"Erreur dans la boucle de contrôle: {e}")
        finally:
            # Nettoyage en cas d'arrêt
            self.arreter()
    
    def demarrer(self):
        """Démarre le système de gestion d'énergie"""
        if not self.running:
            self.running = True
            # Lancer la boucle de contrôle dans un thread séparé
            self.thread_controle = threading.Thread(target=self.executer_boucle_controle)
            self.thread_controle.daemon = True
            self.thread_controle.start()
            logger.info("Système de gestion d'énergie démarré")
    
    def arreter(self):
        """Arrête le système de gestion d'énergie en toute sécurité"""
        self.running = False
        # Désactiver tous les relais
        for source in self.sources_actives:
            self.activer_relais(source, False)
        self.activer_pompe(False)
        logger.info("Système de gestion d'énergie arrêté")
    
    def nettoyer(self):
        """Nettoie les ressources GPIO utilisées"""
        GPIO.cleanup()
        logger.info("Ressources GPIO libérées")


def main():
    """Fonction principale du programme"""
    try:
        # Créer une instance du système
        system = EnergyManagementSystem()
        
        # Démarrer le système
        system.demarrer()
        
        # Maintenir le programme en vie jusqu'à interruption
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Programme interrompu par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
    finally:
        if 'system' in locals():
            system.arreter()
            system.nettoyer()


if __name__ == "__main__":
    main()