# create-app-savane

**create-app-savane** est un générateur d’application Django personnalisée, conçu pour créer rapidement une structure claire, modulaire et professionnelle d’app Django, avec les bons dossiers et fichiers dès le départ.

---

## ✨ Fonctionnalités

- Génère une app Django prête à l’emploi
- Crée des dossiers `models/` et `views/` au lieu des fichiers `models.py` et `views.py`
- Crée automatiquement :
  - `urls.py`
  - `admin.py`
  - `apps.py`
  - `tests.py`
  - le dossier `migrations/` avec son `__init__.py`
  - les dossiers `templates/` et `static/` et un sous dossiers `blog/` (nom_app) contenant par defaut respectivement les fichiers `index.html` et `style.css` les contenant selon les dossiers pères (templates/ et static/)
- Fonctionne avec n’importe quel projet Django

---

## 📦 Installation

Pour installer ce package depuis PyPI :

```bash
- pip install create-app-savane

## Utilisation

Une fois installé, utilisez la commande suivante pour créer une nouvelle application Django :

- create-app nom_de_mon_app
            ou
- create-app 'nom de mon app'; si tu as un groupe de mots les ('') sont necessaires pour ne pas que le 'terminal' affiche une erreur à cause des espaces ou des caractères comme #, !, /...

## Exemple 

- create-app blog


Cela va générer un dossier blog/ avec la structure suivante :

blog/
├── __init__.py
├── admin.py
├── apps.py
├── urls.py
├── tests.py
├── migrations/
│   └── __init__.py
├── models/
│   └── __init__.py
├── views/
│   └── __init__.py
├── static/
│   └── blog/
│       └── style.css
├── templates/
│   └── blog/
│        └── index.html



## 🧠 Comment ça fonctionne ?

La commande `create-app` :

Crée un dossier portant le nom de l’application tout en respectant le snake_case, quelque soit ce que l'utilisateur saisi du moins que les mots collés ou reliés d'une manière au l'autre.
Génère les sous-dossiers models/, views/, migrations/ (avec leurs __init__.py respectifs) et les dossiers templates et static.
Crée les fichiers essentiels à une app Django : admin.py, apps.py, tests.py, urls.py.
Prépare une app prête à être intégrée dans un projet Django existant.


## 🔧 Intégration dans un projet Django

Voici un exemple d'utilisation :

django-admin startproject monprojet
cd monprojet
create-app boutique

Puis, dans monprojet/settings.py, ajoute 'boutique' à la liste INSTALLED_APPS :

INSTALLED_APPS = [
    ...
    'boutique',
]


## ✅ Avantages

Gagnez du temps à chaque création d'application Django
Structure claire et modulaire
Prêt pour des projets évolutifs ou en équipe


🧑‍💻 Auteur

SAVANE Mouhamed
📧 savanemouhamed05@gmail.com
🛠️ Licence : MIT
🌍 Côte d’Ivoire

📚 Exigences

Python ≥ 3.6
Django ≥ 3.2 recommandé