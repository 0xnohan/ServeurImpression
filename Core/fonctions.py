import requests
import socket
import os
import json
from datetime import datetime

# =============================================================================
# FONCTION LOG.TXT
# =============================================================================

def log_message(message):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(base_dir, "..", "data", "log.txt")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)
            
    except Exception as e:
        print(f"Impossible d'écrire dans le fichier log : {e}")
        print(f"Message original: {message}")


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

# Obtenir l'adresse IP locale de la machine
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    
    except Exception as e:
        log_message(f"[FONCTION]: Erreur lors de la récupération de l'adresse IP: {e}")
        return None
      
# Charger la configuration depuis le fichier config.json    
def charger_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "..", "data", "config.json")
    
    if not os.path.exists(config_path):
        log_message(f"[FONCTION]: Le fichier de configuration est introuvable à {config_path}")
        return None
    else: 
        with open(config_path, 'r') as f:
            config = json.load(f)
    return config


# =============================================================================
# FONCTIONS D'IMPRESSION
# =============================================================================

# Télécharger un fichier PDF depuis le serveur
def telecharger_fichier(url_serveur, ip, type_fichier):
    extension = 'pdf' if type_fichier == 'PDF' else 'txt'
    prefixs = ["print_","ticket_"]
    nom_fichier = f"{ip}.{extension}"
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        fichiers_dir = os.path.join(base_dir, "..", "data", "fichiers")
        os.makedirs(fichiers_dir, exist_ok=True)

        for prefix in prefixs:
            nom_fichier_final = f"{prefix}{nom_fichier}"
            url_complete = f"{url_serveur}{nom_fichier_final}"

            try:
                requete = requests.head(url_complete)

                if requete.status_code == 200:
                    reponse = requests.get(url_complete)
                    chemin_destination = os.path.join(fichiers_dir, nom_fichier_final)
                    with open(chemin_destination, 'wb') as f:
                        f.write(reponse.content)
                    return chemin_destination

            except requests.exceptions.RequestException:
                log_message(f"[FONCTION]: Erreur lors de la requête {url_complete}: {e}")
                continue
        return None

    except Exception as e:
        log_message(f"[FONCTION]: Erreur inattendue dans la fonction de téléchargement: {e}")
        return None
