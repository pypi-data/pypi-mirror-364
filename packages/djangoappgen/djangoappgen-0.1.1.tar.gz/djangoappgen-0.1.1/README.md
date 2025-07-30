#  DjangoAppGen

**DjangoAppGen** est un générateur automatique d’applications Django. Il vous permet de créer rapidement la structure d’une app Django complète, prête à l’emploi, avec tous les fichiers essentiels déjà configurés.

---

##  Fonctionnalités

- Création rapide d'une application Django
- Génération automatique des fichiers :
  - `models.py`
  - `views.py`
  - `forms.py`
  - `urls.py`
  - `admin.py`
  - `tests.py`
-  Ajout automatique au `INSTALLED_APPS`
- Interface en ligne de commande simple et rapide
- Personnalisation possible de la structure

---

##  Installation

Assurez-vous d’avoir Python ≥ 3.7 installé.

```bash
pip install djangoappgen

## Utilisation

Pour générer une nouvelle application Django, utilisez la commande suivante :

```bash
python -m djangoappgen.generator nom_de_votre_app

Exemple:
python -m djangoappgen.generator acceuil

