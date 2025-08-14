Fonctionnalités implementées:

- Interface utilisateur identique à celle actuelle
- Sauvegarde des paramètres utilisateurs dans un fichier de config (config.json)
- Fichier serveur principal qui boucle sur les sections d'imprimantes et le TPE
- Fichier fonctions:
    - Fonctions logMessage: elle est appelé à chaque conditions des fonctions du projets et écris les logs/problèmes dans un fichier log.txt
    - getIP: récupère l'ip de la machine actuel (bibliothèque python, fonctionne sur n'importe quel os)
    - chargerConfig: rècupère le fichier json, l'ouvre et le renvoie pour pouvoir le parcourir
    - telechargerFichier: download le fichier sur le serveur dans un dossier local "fichiers" et retourne le chemin du fichier
    - imprimerFichier: récupère la config de l'imprimante,  le basename du chemin fichier et envoie le fichier à l'imprimante définie selon le système d'exploitation
    - supprimerFichier: envoie la requete de supression du fichier au serveur et supprime le fichier en local

- Fichier fonctionIMPR:
    - Regarde le système d'exploitation et récupère la dépendance necessaire (Windows/linux/mac)
    - Fonction listeImprimantes: renvoie une liste des imprimantes réseau ET filaire selon le système d'exploitation
    - Fonctions d'impression spécifiques aux différents SE et pour l'impression ticket


Fonctionnalités à ajouter:
- Test des fonctions TPE partiellement implémentées
- Ajout d'une fonction pour le TPE en série (fonctions.py)
- Ajout d'une fonction pour le LCD (fonctions.py + ajout dans boucle serveur.py)
- Ajout d'une fonction d'impression ticket pour Linux et Mac (fonctionsIMPR.py)
- Ajout d'un champs de saisie similaire au imprimantes pour la récupération du fichier tpe_xxxxx.pdf (Auto IP ou Saisie)(app.py et fonctions.py)
- Eventuellement changer le nom des "values" des boutons/champs de saisis lors de la sauvegarde dans le fichier json pour être plus clair(status, type(txt,pdf,Desactiver), mode(TPV IP,Serie))