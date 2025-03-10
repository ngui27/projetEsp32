#!/usr/bin/env python3
import subprocess
import serial.tools.list_ports
import yaml
import os

# Chemin où le fichier YAML temporaire sera généré
CONFIG_PATH = "config/esphome_config/esp32_initial_config.yaml"
# Commande ESPHome pour compiler et flasher (ajustez selon votre installation)
ESPHOME_CMD = ["esphome", "run", CONFIG_PATH]

def find_esp32():
    ports = serial.tools.list_ports.comports()
    print("Ports détectés :")
    for port in ports:
        print(f"- {port.device} : {port.description}")
        if "USB" in port.description or "CH340" in port.description or "CP210" in port.description:
            return port.device
    return None

def generate_initial_config():
    # Configuration ESPHome initiale pour détecter les capteurs sur plusieurs GPIO
    config = {
        "esphome": {
            "name": "esp32_sensor_detector",
            "friendly_name": "Détecteur de capteurs ESP32"
        },
        "esp32": {
            "board": "esp32dev",
            "framework": {"type": "arduino"}
        },
        "logger": {},
        "api": {"encryption": {"key": "GL76O9M7dR7RXvLV9glBaXb0OMJVmfy8wjy/+iI+vKE="}},
        "ota": {"platform": "esphome", "password": "c8c904f0b4be4fb42770692e07b57695"},
        "wifi": {
            "ssid": "!secret wifi_ssid",
            "password": "!secret wifi_password",
            "fast_connect": True,
            "manual_ip": {
                "static_ip": "192.168.0.83",
                "gateway": "192.168.0.1",
                "subnet": "255.255.255.0"
            },
            "ap": {"ssid": "ESP32 Fallback Hotspot", "password": "pv3VYxQMKQUE"}
        },
        "sensor": []
    }

    # Liste des GPIO à scanner pour détecter les capteurs
    gpio_pins = ["GPIO34", "GPIO35", "GPIO33", "GPIO32", "GPIO36", "GPIO25", "GPIO26", "GPIO27", "GPIO14", "GPIO13"]

    # Ajouter un capteur ADC pour chaque GPIO
    for i, pin in enumerate(gpio_pins, 1):
        config["sensor"].append({
            "platform": "adc",
            "pin": pin,
            "name": f"Tension Capteur {i} (Détection)",
            "id": f"tension_capteur_{i}",
            "unit_of_measurement": "V",
            "update_interval": "5s",
            "attenuation": "12db",
            "filters": [
                {"median": {"window_size": 5, "send_every": 1, "send_first_at": 1}}
            ]
        })

    # Créer le dossier config/esphome_config s'il n'existe pas
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    # Écrire la configuration dans un fichier YAML
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"Configuration initiale générée : {CONFIG_PATH}")

def configure_esp32(port):
    if port:
        print(f"ESP32 détecté sur {port}, génération de la configuration initiale...")
        generate_initial_config()
        print(f"Flashing de la configuration sur {port}...")
        try:
            subprocess.run(ESPHOME_CMD, check=True)
            print("Configuration initiale flashée avec succès !")
            print("L'ESP32 devrait maintenant se connecter au WiFi et envoyer les données à Home Assistant.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors du flashage : {e}")
    else:
        print("Aucun ESP32 détecté.")

if __name__ == "__main__":
    ESP_PORT = find_esp32()
    configure_esp32(ESP_PORT)