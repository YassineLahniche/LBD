#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRIPT DE CALIBRATION ET TEST DES COMPOSANTS
===========================================
Ce script permet de tester individuellement les capteurs ACS712 et les relais
du système de gestion d'énergie, puis de les calibrer pour des mesures précises.

Fonctionnalités:
- Test de communication avec l'ADC ADS1115
- Test individuel de chaque relais
- Lecture des valeurs brutes des capteurs de courant
- Assistant de calibration pour les capteurs ACS712
- Vérification d'exclusion mutuelle des relais

Auteur: [Votre nom]
Date: 20 avril 2025
"""

import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import json
import os
import sys

# Définition des pins GPIO pour les relais
RELAY_PINS = {
    'solaire': 17,
    'eolienne': 27,
    'fossile': 22,
    'circuit1': 23,
    'circuit2': 24
}

# Configuration des canaux ADC pour les capteurs
ADC_CHANNELS = {
    'solaire': ADS.P0,
    'eolienne': ADS.P1,
    'fossile': ADS.P2,
    'sortie': ADS.P3
}

# Fichier pour stocker les résultats de calibration
CALIBRATION_FILE = "calibration_data.json"

class CalibrationSystem:
    """Système de calibration et test des composants"""
    
    def __init__(self):
        """Initialise le système de calibration"""
        print("\n--- INITIALISATION DU SYSTÈME DE CALIBRATION ---")
        
        # Configuration GPIO
        GPIO.setmode(GPIO.BCM)
        for pin in RELAY_PINS.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)  # Tous les relais désactivés au démarrage
            
        # Configuration I2C et ADS1115
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS.ADS1115(self.i2c)
            print("✅ ADS1115 détecté et initialisé avec succès")
        except Exception as e:
            print(f"❌ ERREUR: ADS1115 non détecté: {e}")
            print("Vérifiez les connexions I2C et exécutez 'i2cdetect -y 1'")
            sys.exit(1)
            
        # Configuration des capteurs
        self.sensors = {}
        for name, channel in ADC_CHANNELS.items():
            try:
                self.sensors[name] = AnalogIn(self.ads, channel)
                print(f"✅ Capteur {name} connecté au canal {channel}")
            except Exception as e:
                print(f"❌ ERREUR: Impossible de configurer le capteur {name}: {e}")
        
        # Chargement des données de calibration précédentes (si elles existent)
        self.calibration_data = {
            'offsets': {
                'solaire': 2.5,
                'eolienne': 2.5,
                'fossile': 2.5,
                'sortie': 2.5
            },
            'factors': {
                'solaire': 0.185,  # ACS712 5A: 185mV/A
                'eolienne': 0.185, # ACS712 5A: 185mV/A
                'fossile': 0.066,  # ACS712 30A: 66mV/A
                'sortie': 0.066    # ACS712 30A: 66mV/A
            }
        }
        
        self.load_calibration()
        print("\nSystème de calibration prêt à l'emploi.")
    
    def load_calibration(self):
        """Charge les données de calibration depuis le fichier"""
        if os.path.exists(CALIBRATION_FILE):
            try:
                with open(CALIBRATION_FILE, 'r') as f:
                    loaded_data = json.load(f)
                    self.calibration_data.update(loaded_data)
                print(f"✅ Données de calibration chargées depuis {CALIBRATION_FILE}")
            except Exception as e:
                print(f"⚠️ Impossible de charger les données de calibration: {e}")
    
    def save_calibration(self):
        """Enregistre les données de calibration dans un fichier"""
        try:
            with open(CALIBRATION_FILE, 'w') as f:
                json.dump(self.calibration_data, f, indent=4)
            print(f"✅ Données de calibration enregistrées dans {CALIBRATION_FILE}")
        except Exception as e:
            print(f"❌ ERREUR: Impossible d'enregistrer les données de calibration: {e}")
    
    def test_relays(self):
        """Teste chaque relais individuellement"""
        print("\n--- TEST DES RELAIS ---")
        print("Chaque relais sera activé pendant 2 secondes puis désactivé.")
        
        input("Appuyez sur Entrée pour commencer le test des relais...")
        
        for name, pin in RELAY_PINS.items():
            print(f"\nTest du relais {name} (GPIO {pin})...")
            GPIO.output(pin, GPIO.HIGH)
            print(f"  Relais {name} ACTIVÉ")
            time.sleep(2)
            GPIO.output(pin, GPIO.LOW)
            print(f"  Relais {name} DÉSACTIVÉ")
            
            response = input("Le relais a-t-il fonctionné correctement? (O/n): ").strip().lower()
            if response == 'n':
                print(f"❌ Problème détecté avec le relais {name}. Vérifiez les connexions.")
            else:
                print(f"✅ Relais {name} fonctionne correctement")
        
        print("\nTest des relais terminé.")
    
    def test_sensors(self):
        """Affiche les valeurs brutes des capteurs"""
        print("\n--- TEST DES CAPTEURS ---")
        print("Lecture des valeurs brutes des capteurs pendant 10 secondes.")
        print("Assurez-vous qu'aucun courant ne circule dans les capteurs.\n")
        
        print("Capteur     | Tension (V) | Valeur brute | Courant estimé (A)")
        print("-" * 60)
        
        start_time = time.time()
        while time.time() - start_time < 10:
            for name, sensor in self.sensors.items():
                voltage = sensor.voltage
                raw = sensor.value
                offset = self.calibration_data['offsets'][name]
                factor = self.calibration_data['factors'][name]
                
                current = (voltage - offset) / factor
                
                print(f"{name:10} | {voltage:.3f}V     | {raw:6d}      | {current:.3f}A", end="\r")
                time.sleep(0.5)
            print(" " * 70, end="\r")
        
        print("\n\nTest des capteurs terminé.")
    
    def calibrate_zero_offset(self):
        """Calibre les offsets des capteurs à 0A"""
        print("\n--- CALIBRATION DU POINT ZÉRO ---")
        print("Cette étape mesure la tension des capteurs quand aucun courant ne circule.")
        print("IMPORTANT: Assurez-vous qu'aucun courant ne circule dans les capteurs.\n")
        
        input("Appuyez sur Entrée quand vous êtes prêt...")
        
        for name, sensor in self.sensors.items():
            print(f"\nCalibration du capteur {name}...")
            
            # Moyenne sur 10 mesures pour plus de précision
            sum_voltage = 0
            for i in range(10):
                sum_voltage += sensor.voltage
                time.sleep(0.1)
                print(".", end="", flush=True)
            
            avg_voltage = sum_voltage / 10
            self.calibration_data['offsets'][name] = avg_voltage
            
            print(f"\n✅ Offset du capteur {name} calibré à {avg_voltage:.3f}V")
        
        self.save_calibration()
        print("\nCalibration du point zéro terminée.")
    
    def calibrate_with_known_current(self):
        """Calibre les facteurs de conversion avec un courant connu"""
        print("\n--- CALIBRATION AVEC COURANT CONNU ---")
        print("Cette étape ajuste les facteurs de conversion des capteurs.")
        print("Vous aurez besoin d'une charge connue et d'un multimètre.\n")
        
        for name, sensor in self.sensors.items():
            print(f"\nCalibration du capteur {name}:")
            
            proceed = input(f"Voulez-vous calibrer le capteur {name}? (o/N): ").strip().lower()
            if proceed != 'o':
                print(f"Calibration de {name} ignorée.")
                continue
            
            print("\nÉtapes:")
            print("1. Connectez une charge connue au circuit")
            print("2. Mesurez le courant réel avec un multimètre")
            print("3. Entrez la valeur mesurée\n")
            
            input("Appuyez sur Entrée quand la charge est connectée...")
            
            # Moyenne sur 10 mesures pour la tension
            sum_voltage = 0
            for i in range(10):
                sum_voltage += sensor.voltage
                time.sleep(0.1)
                print(".", end="", flush=True)
            
            avg_voltage = sum_voltage / 10
            offset = self.calibration_data['offsets'][name]
            
            try:
                real_current = float(input("\nEntrez le courant mesuré avec le multimètre (en ampères): "))
                
                if real_current <= 0:
                    print("⚠️ La valeur doit être positive. Calibration ignorée.")
                    continue
                
                # Calcul du nouveau facteur de conversion
                factor = (avg_voltage - offset) / real_current
                self.calibration_data['factors'][name] = factor
                
                print(f"✅ Facteur de conversion pour {name}: {factor:.6f}V/A")
            except ValueError:
                print("❌ Valeur invalide entrée. Calibration ignorée.")
        
        self.save_calibration()
        print("\nCalibration avec courant connu terminée.")
    
    def test_readings(self):
        """Affiche les lectures avec les valeurs calibrées"""
        print("\n--- VÉRIFICATION DES LECTURES CALIBRÉES ---")
        print("Affichage des lectures de courant avec les paramètres calibrés.")
        print("Appuyez sur Ctrl+C pour arrêter.\n")
        
        print("Capteur     | Tension (V) | Offset (V) | Facteur (V/A) | Courant (A)")
        print("-" * 75)
        
        try:
            while True:
                for name, sensor in self.sensors.items():
                    voltage = sensor.voltage
                    offset = self.calibration_data['offsets'][name]
                    factor = self.calibration_data['factors'][name]
                    
                    current = (voltage - offset) / factor
                    
                    print(f"{name:10} | {voltage:.3f}V     | {offset:.3f}V    | {factor:.6f}      | {current:.3f}A", end="\r")
                    time.sleep(0.5)
                print(" " * 75, end="\r")
        except KeyboardInterrupt:
            print("\n\nTest des lectures terminé.")
    
    def test_mutual_exclusion(self):
        """Vérifie que les relais sources ne peuvent pas être activés simultanément"""
        print("\n--- TEST D'EXCLUSION MUTUELLE DES RELAIS ---")
        print("Vérification que les relais de sources d'énergie ne peuvent pas être activés en même temps.\n")
        
        source_relays = ['solaire', 'eolienne', 'fossile']
        
        for i, source1 in enumerate(source_relays):
            for source2 in source_relays[i+1:]:
                print(f"Test d'exclusion mutuelle: {source1} et {source2}")
                
                # Activer le premier relais
                GPIO.output(RELAY_PINS[source1], GPIO.HIGH)
                print(f"  Relais {source1} activé")
                time.sleep(1)
                
                # Tenter d'activer le second relais tout en gardant le premier actif
                print(f"  Tentative d'activation de {source2} alors que {source1} est actif...")
                GPIO.output(RELAY_PINS[source2], GPIO.HIGH)
                time.sleep(1)
                
                # Vérifier l'état des relais
                print("  Vérification visuelle:")
                print(f"  - Le relais {source1} doit être ON")
                print(f"  - Le relais {source2} doit être ON")
                
                result = input("  Les deux relais sont-ils activés? (o/N): ").strip().lower()
                if result == 'o':
                    print(f"⚠️ ALERTE: Les relais {source1} et {source2} peuvent être activés simultanément!")
                    print("  Cela pourrait provoquer des courts-circuits. Vérifiez la logique du code principal.")
                else:
                    print(f"✅ Test d'exclusion mutuelle réussi: Un seul relais à la fois est activé")
                
                # Désactiver les deux relais
                GPIO.output(RELAY_PINS[source1], GPIO.LOW)
                GPIO.output(RELAY_PINS[source2], GPIO.LOW)
                print("  Tous les relais désactivés")
                time.sleep(1)
        
        print("\nTest d'exclusion mutuelle terminé.")
    
    def run_all_tests(self):
        """Exécute tous les tests et calibrations"""
        try:
            self.test_relays()
            self.test_sensors()
            self.calibrate_zero_offset()
            self.calibrate_with_known_current()
            self.test_readings()
            self.test_mutual_exclusion()
            
            print("\n====================================")
            print("✅ TOUS LES TESTS SONT TERMINÉS ✅")
            print("====================================")
            print("Les données de calibration ont été enregistrées dans:", CALIBRATION_FILE)
            print("Vous pouvez maintenant utiliser ces valeurs dans votre système principal.")
            
        except KeyboardInterrupt:
            print("\n\nTests interrompus par l'utilisateur.")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Nettoie les ressources utilisées"""
        GPIO.cleanup()
        print("\nNettoyage des pins GPIO effectué.")

def show_menu():
    """Affiche le menu principal"""
    print("\n====================================")
    print("SYSTÈME DE CALIBRATION ET TEST")
    print("====================================")
    print("1. Tester les relais")
    print("2. Tester les capteurs (valeurs brutes)")
    print("3. Calibrer le point zéro (0A)")
    print("4. Calibrer avec un courant connu")
    print("5. Vérifier les lectures calibrées")
    print("6. Tester l'exclusion mutuelle des relais")
    print("7. Exécuter tous les tests")
    print("8. Quitter")
    print("====================================")
    return input("Choisissez une option (1-8): ")

def main():
    """Fonction principale"""
    print("\n======================================================")
    print("SYSTÈME DE CALIBRATION ET TEST DES COMPOSANTS")
    print("======================================================")
    print("Ce programme va vous guider dans la vérification et la")
    print("calibration des capteurs et relais de votre système de")
    print("gestion d'énergie.")
    print("======================================================")
    
    system = CalibrationSystem()
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            system.test_relays()
        elif choice == '2':
            system.test_sensors()
        elif choice == '3':
            system.calibrate_zero_offset()
        elif choice == '4':
            system.calibrate_with_known_current() 
        elif choice == '5':
            system.test_readings()
        elif choice == '6':
            system.test_mutual_exclusion()
        elif choice == '7':
            system.run_all_tests()
        elif choice == '8':
            print("\nFermeture du programme...")
            system.cleanup()
            break
        else:
            print("\nOption invalide. Veuillez réessayer.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        GPIO.cleanup()