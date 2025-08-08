import platform
import subprocess
import time

# =============================================================================
# RECUPERATION DU SYSTEME D'EXPLOITATION
# =============================================================================

try:
    import win32print #type: ignore
    import win32api   #type: ignore

except ImportError:
    win32print = None
    win32api = None

try:
    import serial     #type: ignore
except ImportError:
    serial = None


# =============================================================================
# FONCTIONS LISTE LOCALE IMPRIMANTES
# =============================================================================

def listeImprimantes():
    systeme = platform.system()
    imprimantes = []

    if systeme == "Windows":
        try:
            if not win32print:
                raise ImportError("Le module pywin32 n'est pas installé")

            imprimantes_info = win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS,
                None,
                1
            )
            imprimantes = [imprimante['pName'] for imprimante in imprimantes_info]
        except ImportError:
            None
    
    elif systeme in ["Linux", "Darwin"]:  
        try:
            resultat = subprocess.run(["lpstat", "-e"], capture_output=True, text=True)
            if resultat.returncode == 0:
                lignes = resultat.stdout.strip().split('\n')
                imprimantes = [ligne.strip() for ligne in lignes if ligne.strip()]
            else:
                print("Impossible de récupérer les imprimantes. lpstat non disponible ou service CUPS non actif")
        except FileNotFoundError:
            print("lpstat est introuvable. Assurez-vous que CUPS est installé (sudo apt install cups)")

    return imprimantes


# =============================================================================
# FONCTIONS D'IMPRESSION
# =============================================================================

def imprimerWindows(chemin_fichier, nom_imprimante):
    try:
        win32api.ShellExecute(0, "print", chemin_fichier, f'"{nom_imprimante}"', ".", 0)
        return True
    # confirmation de l'impression réussie
    except Exception as e:
        print(f"Erreur d'impression Windows sur '{nom_imprimante}': {e}")
        return False


def imprimerLM(chemin_fichier, nom_imprimante):
    try:
        subprocess.run(["lp", "-d", nom_imprimante, chemin_fichier], check=True, capture_output=True)
        return True
    except FileNotFoundError:
        print(f"Erreur d'impression sur '{nom_imprimante}'")
        return False
        
def imprimerSerie(chemin_fichier, port, vitesse):
    if not serial:
        print("Erreur: Le module pyserial n'est pas disponible pour l'impression série")
        return False
    try:
        with serial.Serial(port, int(vitesse), timeout=2) as ser:
            with open(chemin_fichier, 'rb') as f: 
                ser.write(f.read())
            time.sleep(1) 
        return True
    except serial.SerialException as e:
        print(f"Erreur de port série sur '{port}': {e}")
        return False
    except Exception as e:
        print(f"Erreur lors de l'impression série: {e}")
        return False
