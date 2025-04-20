import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Configuration des broches GPIO
RELAY_1_PIN = 17
RELAY_2_PIN = 18

# Paramètres du système
SEUIL_HAUT = 2.0  # Ampères - à ajuster selon vos besoins
SEUIL_BAS = 1.5   # Ampères - à ajuster selon vos besoins
DELAI_LECTURE = 0.5  # Secondes entre chaque lecture
HYSTERESIS = 0.2  # Valeur d'hystérésis pour éviter les oscillations

# Configuration de l'ADC (ADS1115) via I2C
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# Configuration des canaux pour les capteurs de courant
current_sensor_1 = AnalogIn(ads, ADS.P0)  # Capteur primaire sur A0
current_sensor_2 = AnalogIn(ads, ADS.P1)  # Capteur secondaire sur A1

class EnergyController:
    def __init__(self):
        # Configuration du GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAY_1_PIN, GPIO.OUT)
        GPIO.setup(RELAY_2_PIN, GPIO.OUT)
        
        # État initial
        self.relay_1_active = False
        self.relay_2_active = False
        
        # Désactiver les deux relais au démarrage pour sécurité
        GPIO.output(RELAY_1_PIN, GPIO.LOW)
        GPIO.output(RELAY_2_PIN, GPIO.LOW)
        
        print("Système de contrôle d'énergie initialisé")
    
    def activer_relay_1(self):
        """Active Relay 1 et désactive Relay 2"""
        if not self.relay_1_active:
            print("Activation de Relay 1")
            # Désactiver Relay 2 d'abord pour éviter toute activation simultanée
            GPIO.output(RELAY_2_PIN, GPIO.LOW)
            time.sleep(0.1)  # Petit délai de sécurité
            GPIO.output(RELAY_1_PIN, GPIO.HIGH)
            self.relay_1_active = True
            self.relay_2_active = False
    
    def activer_relay_2(self):
        """Active Relay 2 et désactive Relay 1"""
        if not self.relay_2_active:
            print("Activation de Relay 2")
            # Désactiver Relay 1 d'abord pour éviter toute activation simultanée
            GPIO.output(RELAY_1_PIN, GPIO.LOW)
            time.sleep(0.1)  # Petit délai de sécurité
            GPIO.output(RELAY_2_PIN, GPIO.HIGH)
            self.relay_2_active = True
            self.relay_1_active = False
    
    def lire_courant_entree(self):
        """Lit la valeur du capteur de courant d'entrée et la convertit en ampères"""
        # Conversion supposée - à ajuster selon votre capteur spécifique
        raw_value = current_sensor_1.value
        voltage = current_sensor_1.voltage
        
        # Exemple de calcul pour un capteur ACS712 (30A)
        # Coefficient à ajuster selon votre capteur
        amperes = (voltage - 2.5) / 0.066  
        
        return amperes
    
    def lire_courant_sortie(self):
        """Lit la valeur du capteur de courant de sortie et la convertit en ampères"""
        # Conversion supposée - à ajuster selon votre capteur spécifique
        raw_value = current_sensor_2.value
        voltage = current_sensor_2.voltage
        
        # Exemple de calcul pour un capteur ACS712 (30A)
        # Coefficient à ajuster selon votre capteur
        amperes = (voltage - 2.5) / 0.066
        
        return amperes
    
    def executer_controle(self):
        """Exécute l'algorithme de contrôle principal"""
        try:
            # Lecture initiale
            courant_entree = self.lire_courant_entree()
            print(f"Courant d'entrée initial: {courant_entree:.2f}A")
            
            while True:
                # Lire le courant d'entrée
                courant_entree = self.lire_courant_entree()
                print(f"Courant d'entrée: {courant_entree:.2f}A")
                
                # Logique de contrôle avec hystérésis
                if courant_entree > (SEUIL_HAUT + HYSTERESIS) or \
                   (courant_entree > (SEUIL_HAUT - HYSTERESIS) and self.relay_1_active):
                    self.activer_relay_1()
                else:
                    self.activer_relay_2()
                    
                    # Si on utilise Relay 2, surveiller le capteur secondaire
                    if self.relay_2_active:
                        courant_sortie = self.lire_courant_sortie()
                        print(f"Courant de sortie (Relay 2): {courant_sortie:.2f}A")
                        
                        if courant_sortie > SEUIL_BAS:
                            print(f"Courant de sortie trop élevé ({courant_sortie:.2f}A), basculement sur Relay 1")
                            self.activer_relay_1()
                
                # Délai avant la prochaine lecture
                time.sleep(DELAI_LECTURE)
                
        except KeyboardInterrupt:
            print("Arrêt du système demandé par l'utilisateur")
        finally:
            self.nettoyer()
    
    def nettoyer(self):
        """Nettoyage des ressources et retour à l'état sécurisé"""
        print("Nettoyage des ressources...")
        GPIO.output(RELAY_1_PIN, GPIO.LOW)
        GPIO.output(RELAY_2_PIN, GPIO.LOW)
        GPIO.cleanup()
        print("Système arrêté en toute sécurité")

if __name__ == "__main__":
    print("Démarrage du système de contrôle d'énergie...")
    controller = EnergyController()
    controller.executer_controle()