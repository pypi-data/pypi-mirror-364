# dotenv-wizard-savane

**dotenv-wizard-savane** est un outil en ligne de commande (CLI) pour générer automatiquement des fichiers `.env` et `.env.example` en analysant intelligemment le code source de votre projet Python.

Il détecte les variables d'environnement utilisées avec `os.getenv()` et `os.environ[]`, puis crée les fichiers `.env` à partir de ces informations — sans configuration manuelle.

---

## 🚀 Fonctionnalités

- 🔍 Analyse automatique du code source `.py`
- 🧠 Détection des variables utilisées dans :
  - `os.getenv("VAR", default)`
  - `os.environ["VAR"]`
- ✨ Génère deux fichiers :
  - `.env` (avec valeurs par défaut si présentes)
  - `.env.example` (vide pour partage / versioning)
- 🧹 Ignore automatiquement les dossiers inutiles comme `venv/`, `__pycache__/`, `.git/`, `migrations/`, `tests/`
- 📊 Affiche un résumé clair à la fin

---

## 📦 Installation

Depuis [PyPI](https://pypi.org/project/dotenv-wizard-savane/) :

```bash
pip install dotenv-wizard-savane

Ou localement dans un projet :

pip install -e .


🛠️ Utilisation

dotenv-wizard init [chemin]
chemin (optionnel) : chemin du dossier à analyser (par défaut .)


📌 Exemples :
Analyse du dossier courant :

dotenv-wizard init

Analyse d’un sous-dossier spécifique :

dotenv-wizard init backend/


📁 Exemple de résultat

🎯 Code Python analysé :

import os

DEBUG = os.getenv("DEBUG", "false")
PORT = int(os.getenv("PORT", 8000))
SECRET_KEY = os.environ["SECRET_KEY"]
📄 Fichier .env généré :
DEBUG=false
PORT=8000
SECRET_KEY=
📄 Fichier .env.example généré :
DEBUG=
PORT=
SECRET_KEY=


📊 Résumé affiché en CLI

Analyse du dossier : .

Fichiers .env et .env.example générés.

Résumé :
  Fichiers scannés     : 7
  Fichiers ignorés     : 5
  Variables détectées  : 3
  ➤  DEBUG, PORT, SECRET_KEY


🔒 Pourquoi utiliser dotenv-wizard-savane ?

🧠 Zéro configuration, tout est automatique
✅ Gagne du temps et évite les erreurs humaines
🤝 Idéal pour travailler en équipe (génère aussi le .env.example)
📁 Convient aux projets Django, FastAPI, Flask, etc.


📚 Bonnes pratiques recommandées

Ne versionnez jamais le fichier .env (ajoutez-le à votre .gitignore)
Versionnez le fichier .env.example
Utilisez dotenv-wizard-savane à chaque fois que vous ajoutez une nouvelle variable dans le code


⚙️ Fonctionnement interne (pour les curieux)

Utilise des expressions régulières pour détecter :
os.getenv("...") (avec ou sans valeur par défaut)
os.environ["..."]
Ignore les répertoires non pertinents (virtuels, caches, migrations, etc.)
Gère les encodages automatiquement
🧑‍💻 Auteur

SAVANE Mouhamed
📧 savanemouhamed05@gmail.com
🛠️ Licence : MIT
🌍 Côte d’Ivoire