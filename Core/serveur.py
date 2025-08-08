import time
from .fonctions import chargerConfig, getIP, telechargerFichier, logMessage, imprimerFichier, supprimerFichier



prefixeLog = "[SERVEUR]"

# =============================================================================
# PROCESSUS IMPRIMANTE 
# =============================================================================
def traiterImprimante(imprimante_config, url_serveur, auto_ip,):
    type_fichier = imprimante_config.get('type')
    if not type_fichier or type_fichier == 'Desactiver':
        return 

    ip = None
    source_mode = imprimante_config.get('source_mode', 'Auto IP')
    
    if source_mode == 'Auto IP':
        ip = auto_ip
    elif source_mode == 'Manuel':
        ip = imprimante_config.get('source_ip_manuelle')
    
    if not ip:
        return

    fichier_telecharge = telechargerFichier(url_serveur, ip, type_fichier)

    if fichier_telecharge:
        impression_reussie = imprimerFichier(fichier_telecharge, imprimante_config)
        
        if impression_reussie:
            supprimerFichier(fichier_telecharge, url_serveur)
        else:
            logMessage(prefixeLog, "Échec de l'impression")



# =============================================================================
# BOUCLE PRINCIPALE SERVEUR
# =============================================================================
def main():
    print("Serveur d'impression en cours d'exécution...")
    auto_ip = getIP()

    try:
        while True:
            config = chargerConfig()

            if not config:
                logMessage(prefixeLog, "Configuration introuvable ou non définie, nouvel essai dans 10s...")
                time.sleep(10)
                continue

            # Charger la configuration de la section "Serveur"
            serveur_config = config.get('Serveur', {})
            url_serveur = serveur_config.get('url')
            vitesse = serveur_config.get('vitesse_boucle', 1000)
            delai_secondes = vitesse/ 1000

            if not url_serveur:
                logMessage(prefixeLog, "URL du serveur n'est pas définie dans config.json")
                time.sleep(5)
                continue

            # Boucle sur chaque section d'imprimante
            for i in range(1, 6):
                nom_imprimante_section = f'Imprimante{i}'
                if nom_imprimante_section in config:
                    imprimante_config = config[nom_imprimante_section]
                    traiterImprimante(imprimante_config, url_serveur, auto_ip)
            
            time.sleep(delai_secondes)
            
    except Exception as e:
        logMessage(prefixeLog, f"Erreur dans la boucle principale: {e}")
    finally:
        print("Fin du serveur d'impression.")

if __name__ == "__main__":
    main()
