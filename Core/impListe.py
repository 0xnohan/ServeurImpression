import platform
import subprocess

def liste_imprimantes():
    systeme = platform.system()
    imprimantes = []

    if systeme == "Windows":
        try:
            import win32print
            imprimantes_info = win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS,
                None,
                1
            )
            imprimantes = [imprimante['pName'] for imprimante in imprimantes_info]
        except ImportError:
            print("Erreur : le module pywin32 est requis sur Windows. Installez-le avec 'pip install pywin32'.")
    
    elif systeme in ["Linux", "Darwin"]:  # Darwin = macOS
        try:
            resultat = subprocess.run(["lpstat", "-e"], capture_output=True, text=True)
            if resultat.returncode == 0:
                lignes = resultat.stdout.strip().split('\n')
                imprimantes = [ligne.strip() for ligne in lignes if ligne.strip()]
            else:
                print("Impossible de récupérer les imprimantes. lpstat non disponible ou service CUPS non actif.")
        except FileNotFoundError:
            print("Erreur : lpstat est introuvable. Assurez-vous que CUPS est installé (sudo apt install cups).")

    else:
        print(f"Système d'exploitation non supporté : {systeme}")

    return imprimantes
