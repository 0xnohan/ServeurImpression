import time
import os
from fonctions import charger_config, get_ip, telecharger_fichier, log_message

def main():
    print("Serveur d'impression en cours d'exécution...")

    auto_ip = get_ip()

    try:
        while True:
            config = charger_config()
            if not config:
                log_message("[SERVEUR]: Configuration introuvable ou non définie, nouvel essai dans 10s...")
                time.sleep(10)
                continue

            serveur_config = config.get('Serveur', {})
            url_serveur = serveur_config.get('url')
            vitesse = serveur_config.get('vitesse_boucle', 1000)

            if not url_serveur:
                log_message("[SERVEUR]: L'URL du serveur n'est pas définie dans config.json")
                time.sleep(5)
                continue

            #Chaque section d'imprimante
            for i in range(1, 6):
                nom_imprimante = f'Imprimante{i}'
                imprimante_config = config.get(nom_imprimante, {})
                
                type_fichier = imprimante_config.get('type', 'Desactiver')
                if type_fichier == 'Desactiver':
                    continue

                ip = None
                mode_source = imprimante_config.get('source_mode', 'Auto IP')

                if mode_source == 'Auto IP':
                    ip = auto_ip

                elif mode_source == 'Manuel':
                    ip = imprimante_config.get('source_ip_manuelle')
                
                if not ip:
                    log_message(f"[SERVEUR]: IP non définie pour {nom_imprimante}")
                    continue

                fichier_telecharge = telecharger_fichier(url_serveur, ip, type_fichier)

                if fichier_telecharge:
                    pass
                    # La logique d'impression et de suppression sera ajoutée ici
            
            delai_secondes = vitesse / 1000
            time.sleep(delai_secondes)

    except Exception as e:
        log_message(f"[SERVEUR]: Erreur dans la boucle principale: {e}")
    finally:
        print("--- Fin du processus serveur ---")

if __name__ == "__main__":
    main()
