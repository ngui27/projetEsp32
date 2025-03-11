import subprocess
import serial.tools.list_ports
import yaml
import os
import shutil
import socket
import re
import config.esphome_config.logs as logs

# Chemin vers le fichier de configuration ESPHome
CONFIG_PATH = "config/esphome_config/ESP32_initial_config.yaml"

# Dossier pour sauvegarder les informations de l'ESP32
INFO_DIR = "/Users/guilhemlaieb/Documents/Partage/infoesp32"

# Trouve le chemin de la commande 'esphome' dans le système
ESPHOME_PATH = shutil.which("esphome")
if not ESPHOME_PATH:
    raise FileNotFoundError("Impossible de trouver 'esphome' dans le PATH. Assurez-vous qu'il est installé avec 'pip install esphome'.")

# Liste des pins GPIO disponibles pour les capteurs ADC sur ESP32
AVAILABLE_GPIO_PINS = ["GPIO32", "GPIO33", "GPIO34", "GPIO35", "GPIO36", "GPIO39"]

# Crée la commande pour exécuter ESPHome avec le port spécifié
def get_esphome_cmd(port):
    return [ESPHOME_PATH, "run", CONFIG_PATH, "--device", port]

# Recherche l'ESP32 connecté via les ports série
def find_esp32():
    ports = serial.tools.list_ports.comports()
    print("Ports détectés :")
    for port in ports:
        print(f"- {port.device} : {port.description}")
        if "USB" in port.description or "CH340" in port.description or "CP210" in port.description:
            return port.device
    return None

# Obtient l'adresse IP locale de l'ordinateur
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "192.168.0.1"

# Trouve une adresse IP disponible dans le réseau local
def find_available_ip():
    base_ip = re.match(r"(\d+\.\d+\.\d+)\.\d+", get_local_ip()).group(1)
    for i in range(100, 200):
        ip = f"{base_ip}.{i}"
        if not is_ip_in_use(ip):
            return ip
    return f"{base_ip}.250"

# Vérifie si une adresse IP est déjà utilisée
def is_ip_in_use(ip):
    try:
        socket.gethostbyaddr(ip)
        return True
    except socket.herror:
        return False

# Génère la configuration initiale pour l'ESP32
def generate_initial_config(esp_name, num_sensors):
    local_ip = get_local_ip()
    base_ip = re.match(r"(\d+\.\d+\.\d+)\.\d+", local_ip).group(1)
    static_ip = find_available_ip()
    gateway = f"{base_ip}.1"
    subnet = "255.255.255.0"
    result = subprocess.run(['openssl', 'rand', '-base64', '32'], capture_output=True, text=True)
    api_key = result.stdout.strip()

    config = {
        "esphome": {
            "name": esp_name,
            "friendly_name": f"ESP32 {esp_name}"
        },
        "esp32": {
            "board": "esp32dev",
            "framework": {"type": "arduino"}
        },
        "logger": {"level": "DEBUG"},
        "api": {"encryption": {"key": api_key}},
        "ota": {"platform": "esphome", "password": "votre_mot_de_passe_ota"},
        "wifi": {
            "ssid": logs.wifi_ssid,
            "password": logs.wifi_password,
            "fast_connect": True,
            "manual_ip": {
                "static_ip": static_ip,
                "gateway": gateway,
                "subnet": subnet
            },
            "reboot_timeout": "0s",
            "ap": {"ssid": f"{esp_name} Fallback Hotspot", "password": "pv3VYxQMKQUE"}
        },
        "sensor": []
    }

    if num_sensors > len(AVAILABLE_GPIO_PINS):
        print(f"Attention : {num_sensors} capteurs demandés, mais seulement {len(AVAILABLE_GPIO_PINS)} pins disponibles. Limité à {len(AVAILABLE_GPIO_PINS)}.")
        num_sensors = len(AVAILABLE_GPIO_PINS)

    selected_pins = AVAILABLE_GPIO_PINS[:num_sensors]
    for i, pin in enumerate(selected_pins, 1):
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
    print(f"Configuration initiale générée avec {num_sensors} capteurs : {CONFIG_PATH}")
    return api_key

# Sauvegarde les informations dans un fichier
def save_esp_info(esp_name, api_key):
    os.makedirs(INFO_DIR, exist_ok=True)  # Crée le dossier s'il n'existe pas
    file_path = os.path.join(INFO_DIR, f"{esp_name}_info.txt")
    with open(file_path, "w") as f:
        f.write(f"Nom de l'ESP32 : {esp_name}\n")
        f.write(f"Clé API : {api_key}\n")
    print(f"Informations sauvegardées dans : {file_path}")

# Configure et flashe l'ESP32
def configure_esp32(port):
    if port:
        esp_name = input("Entrez le nom de votre ESP32 : ")
        while True:
            try:
                num_sensors = int(input(f"Combien de capteurs GPIO voulez-vous configurer (max {len(AVAILABLE_GPIO_PINS)}) ? "))
                if num_sensors >= 0:
                    break
                print("Veuillez entrer un nombre positif.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")

        print(f"ESP32 détecté sur {port}, génération de la configuration pour {esp_name} avec {num_sensors} capteurs...")
        api_key = generate_initial_config(esp_name, num_sensors)
        print(f"Flashing de la configuration sur {port}...")
        
        # Sauvegarde des informations avant le flashage
        save_esp_info(esp_name, api_key)
        
        try:
            subprocess.run(get_esphome_cmd(port), check=True)
            print("Configuration flashée avec succès !")
            
            import pyperclip
            print("\n--- Résultat ---")
            print(f"Clé API générée : {api_key}")
            pyperclip.copy(api_key)
            print("La clé API a été copiée dans votre presse-papiers !")
            print("Appuyez sur Entrée pour relancer le programme, ou Ctrl+C pour quitter.")
            input()
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors du flashage : {e}")
            print("Appuyez sur Entrée pour relancer le programme, ou Ctrl+C pour quitter.")
            input()
            return True
    else:
        print("Aucun ESP32 détecté.")
        print("Appuyez sur Entrée pour réessayer, ou Ctrl+C pour quitter.")
        input()
        return True

# Point d'entrée principal du script
if __name__ == "__main__":
    try:
        import pyperclip
    except ImportError:
        print("Installation de pyperclip pour copier la clé API...")
        subprocess.run(["pip3", "install", "pyperclip"], check=True)

    while True:
        ESP_PORT = find_esp32()
        if not configure_esp32(ESP_PORT):
            break