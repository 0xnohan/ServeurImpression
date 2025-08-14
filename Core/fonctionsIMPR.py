import platform
import subprocess
import time
import os

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
            imprimantes = [imprimante[2] for imprimante in imprimantes_info]
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
    if not win32print:
        print("Erreur: Le module pywin32 n'est pas disponible pour l'impression Windows.")
        return False

    try:
        hPrinter = win32print.OpenPrinter(nom_imprimante)
        try:
            nom_fichier_base = os.path.basename(chemin_fichier)
            datatype = "RAW"
            
            hJob = win32print.StartDocPrinter(hPrinter, 1, (nom_fichier_base, None, datatype))
            try:
                win32print.StartPagePrinter(hPrinter)
                try:
                    with open(chemin_fichier, "rb") as f:
                        win32print.WritePrinter(hPrinter, f.read())
                finally:
                    win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
        
        return True

    except Exception as e:
        print(f"Erreur d'impression Windows API sur '{nom_imprimante}': {e}")
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


def imprimerTicket(chemin_fichier, nom_imprimante):
    if not win32print:
        print("Erreur: Le module pywin32 n'est pas disponible.")
        return False
    
    CMD_INIT = b'\x1b@'
    CMD_CODEPAGE = b'\x1b\x74\x00'
    CMD_CUT = b'\x1d\x56\x01'

    try:
        hPrinter = win32print.OpenPrinter(nom_imprimante)
        try:
            nom_fichier_base = os.path.basename(chemin_fichier)
            hJob = win32print.StartDocPrinter(hPrinter, 1, (nom_fichier_base, None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                try:
                    with open(chemin_fichier, "r", encoding="utf-8", errors='ignore') as f:
                        text_data = f.read()

                    encoded_data = text_data.encode('cp437', errors='replace')
                    
                    print("Mode Ticket. Encodage en CP437 et ajout des commandes ESC/POS.")
                    donnees_a_imprimer = (
                        CMD_INIT +
                        CMD_CODEPAGE + 
                        encoded_data + 
                        b'\n\n\n\n' +   
                        CMD_CUT
                    )
                    win32print.WritePrinter(hPrinter, donnees_a_imprimer)
                finally:
                    win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
        return True
    except Exception as e:
        print(f"Erreur d'impression Ticket sur '{nom_imprimante}': {e}")
        return False