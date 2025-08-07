import platform
import subprocess

def liste_imprimantes():
    systeme = platform.system()
    imprimantes = []

    if systeme == "Windows":
        try:
            import win32print
            # Inclut imprimantes locales, connectées, et partagées
            flags = (win32print.PRINTER_ENUM_LOCAL |
                     win32print.PRINTER_ENUM_CONNECTIONS |
                     win32print.PRINTER_ENUM_SHARED)
            imprimantes_info = win32print.EnumPrinters(flags, None, 1)
            imprimantes = [imprimante['pName'] for imprimante in imprimantes_info]
        except ImportError:
            print("Erreur : le module pywin32 est requis sur Windows. Installez-le avec 'pip install pywin32'.")

    elif systeme in ["Linux", "Darwin"]:  # macOS = Darwin
        try:
            # Récupère les imprimantes installées via lpstat
            resultat_lpstat = subprocess.run(["lpstat", "-e"], capture_output=True, text=True)
            if resultat_lpstat.returncode == 0:
                lignes = resultat_lpstat.stdout.strip().split('\n')
                imprimantes.extend([ligne.strip() for ligne in lignes if ligne.strip()])
            else:
                print("lpstat ne peut pas lister les imprimantes. Service CUPS peut être inactif.")

            # Récupère les périphériques d'impression (inclut USB, etc.)
            resultat_lpinfo = subprocess.run(["lpinfo", "-v"], capture_output=True, text=True)
            if resultat_lpinfo.returncode == 0:
                lignes = resultat_lpinfo.stdout.strip().split('\n')
                for ligne in lignes:
                    if "usb://" in ligne or "parallel://" in ligne or "serial://" in ligne:
                        imprimantes.append(ligne.strip())
            else:
                print("lpinfo ne peut pas lister les périphériques d'impression.")
        except FileNotFoundError:
            print("Erreur : lpstat ou lpinfo est introuvable. Assurez-vous que CUPS est installé (sudo apt install cups).")


    return list(set(imprimantes)) 

# Exemple d’utilisation
if __name__ == "__main__":
    for imprimante in liste_imprimantes():
        print(f"- {imprimante}")
