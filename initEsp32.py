#!/opt/homebrew/bin/python3.11  # Ajustez selon votre chemin (ex. /usr/local/bin/python3.11)
import subprocess
import serial.tools.list_ports
import yaml
import os
import shutil

# Chemin où le fichier YAML temporaire sera généré
CONFIG_PATH = "config/esphome_config/esp32_initial_config.yaml"

# Trouver dynamiquement le chemin d'esphome
ESPHOME_PATH = shutil.which("esphome")
if not ESPHOME_PATH:
    raise FileNotFoundError("Impossible de trouver 'esphome' dans le PATH. Assurez-vous qu'il est installé avec 'pip install esphome'.")

def get_esphome_cmd(port):
    return [ESPHOME_PATH, "run", CONFIG_PATH, "--device", port]

def find_esp32():
    ports = serial.tools.list_ports.comports()
    print("Ports détectés :")
    for port in ports:
        print(f"- {port.device} : {port.description}")
        if "USB" in port.description or "CH340" in port.description or "CP210" in port.description:
            return port.device
    return None

def generate_initial_config():
    config = {
        "esphome": {
            "name": "esp32-sensor-detector",
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

    gpio_pins = ["GPIO32", "GPIO33", "GPIO34", "GPIO35", "GPIO36", "GPIO39"]
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

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"Configuration initiale générée : {CONFIG_PATH}")

def configure_esp32(port):
    if port:
        print(f"ESP32 détecté sur {port}, génération de la configuration initiale...")
        generate_initial_config()
        print(f"Flashing de la configuration sur {port}...")
        # Vérifier si le port est accessible
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                subprocess.run(get_esphome_cmd(port), check=True)
                print("Configuration initiale flashée avec succès !")
                print("L'ESP32 devrait maintenant se connecter au WiFi et envoyer les données à Home Assistant.")
                break
            except subprocess.CalledProcessError as e:
                if attempt < max_attempts - 1:
                    print(f"Tentative {attempt + 1}/{max_attempts} échouée : {e}. Réessai dans 2 secondes...")
                    time.sleep(2)
                else:
                    print(f"Erreur définitive lors du flashage après {max_attempts} tentatives : {e}")
    else:
        print("Aucun ESP32 détecté.")

if __name__ == "__main__":
    ESP_PORT = find_esp32()
    configure_esp32(ESP_PORT)