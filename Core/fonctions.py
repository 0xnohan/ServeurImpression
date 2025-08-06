import configparser
import requests
import socket
import time
import os


# Obtenir l'adresse IP locale de la machine
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        return f"Erreur : {e}"
    
    
# Charger la configuration depuis le fichier config.ini    
def charger_config():
    config = configparser.ConfigParser()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "..", "config.ini")  
    config.read(config_path)

    url_serveur = config.get("Serveur", "url")
    vitesse = config.getint("Serveur", "vitesse_boucle")

    return url_serveur, vitesse


# Télécharger un fichier PDF depuis le serveur
def telecharger_fichier():
    url_serveur, vitesse = charger_config()
    ip = get_ip()
    url = f"{url_serveur}{ip}.pdf"

    # Créer un répertoire pour stocker les fichiers téléchargés
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fichiers_dir = os.path.join(base_dir, "fichiers")
    os.makedirs(fichiers_dir, exist_ok=True)
    fichier_path = os.path.join(fichiers_dir, f"{ip}.pdf")

    try:
        print(f"Téléchargement du fichier depuis {url}")
        response = requests.get(url, timeout = vitesse)
        with open(fichier_path, 'wb') as f:
            f.write(response.content)
        print("Téléchargement réussi")

    except requests.exceptions.RequestException as e:
        print(f"Échec du téléchargement : {e}")
        return False
    




