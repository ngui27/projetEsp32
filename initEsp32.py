import subprocess
import serial.tools.list_ports
import yaml
import os
import shutil
import socket
import re

CONFIG_PATH = "config/esphome_config/ESP32_initial_config.yaml"
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

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "192.168.0.1"

def find_available_ip():
    base_ip = re.match(r"(\d+\.\d+\.\d+)\.\d+", get_local_ip()).group(1)
    for i in range(100, 200):  # Cherche une IP entre .100 et .199
        ip = f"{base_ip}.{i}"
        if not is_ip_in_use(ip):
            return ip
    return f"{base_ip}.250"

def is_ip_in_use(ip):
    try:
        socket.gethostbyaddr(ip)
        return True
    except socket.herror:
        return False

def generate_initial_config(esp_name):
    static_ip = find_available_ip()
    config = {
        "esphome": {
            "name": esp_name,
            "friendly_name": f"ESP32 {esp_name}"
        },
        "esp32": {
            "board": "esp32dev",
            "framework": {"type": "arduino"}
        },
        "logger": {},
        "api": {"encryption": {"key": "!secret api_key"}},
        "ota": {"platform": "esphome", "password": "!secret ota_password"},
        "wifi": {
            "ssid": "!secret wifi_ssid",
            "password": "!secret wifi_password",
            "fast_connect": True,
            "manual_ip": {
                "static_ip": static_ip,
                "gateway": "192.168.0.1",
                "subnet": "255.255.255.0"
            },
            "reboot_timeout": "0s",
            "ap": {"ssid": f"{esp_name} Fallback Hotspot", "password": "pv3VYxQMKQUE"}
        },
        "sensor": []
    }

    gpio_pins = ["GPIO32", "GPIO33", "GPIO34", "GPIO35", "GPIO36", "GPIO39"]
    for i, pin in enumerate(gpio_pins, 1):
        config["sensor"].append({
            "platform": "adc",
            "pin": pin,
            "name": f"Tension Capteur {i} ({esp_name})",
            "id": f"tension_capteur_{i}",
            "unit_of_measurement": "V",
            "update_interval": "5s",
            "attenuation": "12db",
            "filters": [{"median": {"window_size": 5, "send_every": 1, "send_first_at": 1}}]
        })

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"Configuration initiale générée : {CONFIG_PATH}")

def configure_esp32(port):
    if port:
        esp_name = input("Entrez le nom de votre ESP32 : ")
        print(f"ESP32 détecté sur {port}, génération de la configuration pour {esp_name}...")
        generate_initial_config(esp_name)
        print(f"Flashing de la configuration sur {port}...")
        try:
            subprocess.run(get_esphome_cmd(port), check=True)
            print("Configuration flashée avec succès !")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors du flashage : {e}")
    else:
        print("Aucun ESP32 détecté.")

if __name__ == "__main__":
    ESP_PORT = find_esp32()
    configure_esp32(ESP_PORT)
