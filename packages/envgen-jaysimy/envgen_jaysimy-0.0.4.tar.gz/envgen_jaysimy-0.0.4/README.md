# envgen

envgen est un outil en ligne de commande simple pour générer des fichiers `.env` prêts à l’emploi pour des projets Django ou Flask.

---

## 🔧 Installation

```bash
pip install envgen

###  🔧 Utilisation
m
```bash

envgen <framework_choisi>

"Cela créera un fichier .env dans le dossier courant avec les variables d’environnement de base pour le framework choisi."

"C’est une bibliothèque qui permet à Python de lire le fichier .env."

```bash

pip install python-dotenv

'ensuite ajouter en haut du settings.py:'




import os
from dotenv import load_dotenv

# Charge le fichier .env à la racine du projet
load_dotenv()

# Utilisation des variables
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG") == "True"
