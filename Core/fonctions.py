import requests
import socket
import os
import json
import platform
from datetime import datetime

from .fonctionsIMPR import imprimerWindows, imprimerLM, imprimerSerie, imprimerTicket

prefixeLog = "[FONCTION]"

# =============================================================================
# FONCTION LOG.TXT
# =============================================================================

def logMessage(prefixe, message):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(base_dir, "..", "data", "log.txt")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {prefixe}: {message}\n"
        
        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)
            
    except OSError as e:
        print("Impossible d'écrire dans le fichier log")
        print(f"Message original: {message}")
        print(f"Erreur: {e}")


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

# Obtenir l'adresse IP locale de la machine
def getIP():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    
    except Exception as e:
        logMessage(prefixeLog, f"Erreur lors de la récupération de l'adresse IP: {e}")
        return None
      
# Charger la configuration depuis le fichier config.json    
def chargerConfig():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "..", "data", "config.json")
    
    if not os.path.exists(config_path):
        logMessage(prefixeLog, f"Le fichier de configuration est introuvable à {config_path}")
        return None
    else: 
        with open(config_path, 'r') as f:
            config = json.load(f)
    return config


# =============================================================================
# FONCTIONS D'IMPRESSION
# =============================================================================

# Télécharger un fichier PDF depuis le serveur
def telechargerFichier(url_serveur, ip, extension):
    prefix = ""
    if extension == "pdf":
        prefix = "print_"
    elif extension == "txt":
        prefix = "ticket_"
    elif extension == "php":
        prefix = "tpe_"
    else:
        logMessage(prefixeLog, f"Type de fichier non supporté: {extension}")
        return None
    
    nom_fichier = f"{ip}.{extension}"
    try:
        nom_fichier_final = f"{prefix}{nom_fichier}"
        url_complete = f"{url_serveur}{nom_fichier_final}"

        requete = requests.head(url_complete)

        if requete.status_code == 200:
            reponse = requests.get(url_complete)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            fichiers_dir = os.path.join(base_dir, "..", "data", "fichiers")
            os.makedirs(fichiers_dir, exist_ok=True)

            chemin_destination = os.path.join(fichiers_dir, nom_fichier_final)
            with open(chemin_destination, 'wb') as f:
                f.write(reponse.content)
            #print(chemin_destination)
            return chemin_destination

    except requests.exceptions.RequestException:
        logMessage(prefixeLog, f"Erreur lors de la requête {url_complete}: {e}")
        return None

    except Exception as e:
        logMessage(prefixeLog, f"Erreur inattendue dans la fonction de téléchargement: {e}")
        return None
    
# Imprimer le fichier pdf local
def imprimerFichier(chemin_fichier, imprimante_config):
    nom_imprimante_log = imprimante_config.get('destination', 'N/A')
    destination_mode = imprimante_config.get('destination_mode')
    logMessage(prefixeLog, f"Impression pour '{os.path.basename(chemin_fichier)}' vers '{nom_imprimante_log}' (Mode: {destination_mode})")

    if destination_mode == "Imprimantes":
        destination = imprimante_config.get('destination')
        if not destination:
            logMessage(prefixeLog, "Aucune imprimante de destination n'est configurée")
            return False
        
        systeme = platform.system()
        if systeme == "Windows":
            #print(chemin_fichier)
            if chemin_fichier.lower().endswith(".txt"):
                return imprimerTicket(chemin_fichier, destination)
            else:
              
                return imprimerWindows(chemin_fichier, destination)
           
        else: 
            return imprimerLM(chemin_fichier, destination)

    elif destination_mode == "Série COM":
        port = imprimante_config.get('port_com')
        vitesse = imprimante_config.get('vitesse_com')
        if not port or not vitesse:
            logMessage(prefixeLog, "Le port COM ou la vitesse n'est pas configuré")
            return False
        
        return imprimerSerie(chemin_fichier, port, vitesse)
    
    else:
        logMessage(prefixeLog, f"Mode de destination non supporté: '{destination_mode}'")
        return False
# Supprimer le fichier en local et sur le serveur après impression
def supprimerFichier(chemin_fichier, url_serveur):
    nom_fichier = os.path.basename(chemin_fichier)
    url_delete = f"{url_serveur}/delprint.php?name={nom_fichier}"

    try:
        reponse = requests.get(url_delete, timeout=10)
        reponse.raise_for_status()
        try:
            os.remove(chemin_fichier)

        except OSError as e:
            logMessage(prefixeLog, f"Impossible de supprimer le fichier local {e}")

    except requests.exceptions.RequestException as e:
        logMessage(prefixeLog, f"Impossible de supprimer le fichier serveur '{nom_fichier}': {e}")

# =============================================================================
# FONCTIONS TPE
# =============================================================================

def envoyerReqTpeIp(chemin_fichier, ip, port):
    try:
        
        logMessage("[TPE]", f"Connexion à {ip}:{port}")
        with open(chemin_fichier, "r") as f:
                text_data = f.read()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)  
            s.connect((ip, int(port)))
            s.sendall(text_data.encode())
            logMessage("[TPE]", "Message envoyé avec succès.")
        return True
    except socket.timeout:
        logMessage("[TPE]", f"Erreur: Timeout lors de la connexion à {ip}:{port}")
        return False
    except Exception as e:
        logMessage("[TPE]", f"Erreur de communication TPE IP: {e}")
        return False

def envoyerReqTpeSerie(chemin_fichier, port_com, vitesse, ):
    # pyserial
    pass

#Récupérer le fichier tpe_
def traiterTPE(tpe_config, url_serveur, auto_ip):
    ip_source = auto_ip if tpe_config.get('mode', 'Auto IP') == 'Auto IP' else tpe_config.get('source_ip_manuelle')
    if not ip_source:
        return

    fichier_tpe = telechargerFichier(url_serveur, ip_source, "php")
    
    if fichier_tpe:
        logMessage("[TPE]", f"Fichier de requête TPE trouvé: {fichier_tpe}")
        try:
            with open(fichier_tpe, 'r') as f:
                type_transaction = f.readline().strip()
                montant = f.readline().strip()

            if not montant or not type_transaction:
                logMessage("[TPE]", "Fichier TPE malformé (montant ou type manquant).")
                supprimerFichier(fichier_tpe, url_serveur)
                return

            mode_connexion = tpe_config.get('mode')
            if mode_connexion == 'TPV IP':
                ip_tpe = tpe_config.get('ip_address')
                port_tpe = tpe_config.get('ip_port')
                if ip_tpe and port_tpe:
                    envoyerReqTpeIp(ip_tpe, port_tpe)
                else:
                    logMessage("[TPE]", "Configuration IP du TPE manquante.")

            elif mode_connexion == 'TPV Série COM':
                port_com = tpe_config.get('port_com')
                vitesse_com = tpe_config.get('vitesse_com')
                if port_com and vitesse_com:
                    envoyerReqTpeSerie(port_com, vitesse_com, montant, type_transaction)
                else:
                    logMessage("[TPE]", "Configuration Série du TPE manquante.")
            
            supprimerFichier(fichier_tpe, url_serveur)

        except Exception as e:
            logMessage("[TPE]", f"Erreur lors du traitement du fichier TPE: {e}")
            supprimerFichier(fichier_tpe, url_serveur)
