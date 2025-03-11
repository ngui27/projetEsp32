
# Projet : Initialisation Automatique d'ESP32 avec ESPHome

Ce projet est un script Python conçu pour automatiser la configuration et le flashage d'un microcontrôleur ESP32 lorsqu'il est connecté à un Mac (ou potentiellement Windows) via USB. Il utilise ESPHome pour générer une configuration personnalisée et flasher le firmware, tout en offrant des fonctionnalités pratiques pour gérer les informations de l'appareil.

## Fonctionnalités

- **Détection automatique de l'ESP32** : Identifie l'ESP32 connecté via USB en analysant les ports série disponibles.
- **Configuration personnalisée** :
  - Demande à l'utilisateur un nom unique pour l'ESP32.
  - Permet de spécifier le nombre de capteurs GPIO (ADC) à configurer, en sélectionnant automatiquement les pins disponibles parmi `GPIO32`, `GPIO33`, `GPIO34`, `GPIO35`, `GPIO36`, `GPIO39`.
- **Génération de configuration ESPHome** :
  - Crée un fichier YAML avec une configuration réseau (Wi-Fi avec IP statique), une clé API générée dynamiquement, et des capteurs ADC si spécifiés.
  - Sauvegarde cette configuration dans `config/esphome_config/ESP32_initial_config.yaml`.
- **Flashage automatique** : Utilise la commande `esphome run` pour compiler et flasher la configuration sur l'ESP32.
- **Sauvegarde des informations** :
  - Avant le flashage, enregistre le nom de l'ESP32 et sa clé API dans un fichier texte situé dans `/Users/guilhemlaieb/Documents/Partage/infoesp32/<nom>_info.txt`.
- **Gestion de la clé API** :
  - Affiche la clé API générée après un flashage réussi.
  - Copie automatiquement la clé dans le presse-papiers grâce à `pyperclip`.
- **Relance interactive** : Après chaque exécution (succès ou échec), propose de relancer le script en appuyant sur Entrée, ou de quitter avec `Ctrl+C`.

## Caractéristiques

- **Langage** : Python 3
- **Dépendances** :
  - `serial.tools.list_ports` (via `pyserial`) pour détecter les ports série.
  - `esphome` pour générer et flasher la configuration.
  - `pyperclip` pour copier la clé API dans le presse-papiers (installé automatiquement si absent).
  - `yaml` pour écrire les fichiers de configuration ESPHome.
  - `openssl` (requis sur le système) pour générer des clés API sécurisées.
- **Plateforme cible** : Testé sur macOS, adaptable à Windows avec des ajustements mineurs (ports COM).
- **Chemin de sauvegarde** : Informations stockées dans `/Users/guilhemlaieb/Documents/Partage/infoesp32/`.
- **Configuration réseau** :
  - Assigne une IP statique unique dans la plage `.100` à `.199` du réseau local.
  - Inclut un point d'accès (AP) de secours avec un SSID et mot de passe personnalisés.
- **Capteurs** : Supporte jusqu'à 6 capteurs ADC avec des filtres médians pour des mesures stables.

## Utilisation

1. Branchez un ESP32 via USB à votre Mac.
2. Exécutez le script avec `python3 initEsp32.py`.
3. Suivez les invites :
   - Entrez le nom de l'ESP32.
   - Indiquez le nombre de capteurs GPIO souhaités (0 à 6).
4. Le script :
   - Détecte l'ESP32.
   - Génère et sauvegarde la configuration.
   - Crée un fichier avec le nom et la clé API.
   - Flashe l'ESP32.
   - Affiche et copie la clé API.
5. Appuyez sur Entrée pour relancer ou `Ctrl+C` pour quitter.

## Prérequis

- Python 3 installé.
- ESPHome installé (`pip3 install esphome`).
- OpenSSL installé (préinstallé sur macOS, ou via Homebrew avec `brew install openssl` si nécessaire).
- Accès en écriture au dossier `/Users/guilhemlaieb/Documents/Partage/infoesp32/`.

## Exemple de fichier généré

Fichier : `/Users/guilhemlaieb/Documents/Partage/infoesp32/mon_esp32_info.txt`
