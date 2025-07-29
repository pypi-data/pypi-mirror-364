# Application To-Do List Django

## Description

Cette application Django permet de gérer une liste simple de tâches.  
Elle propose une interface web pour afficher la liste des tâches, ainsi qu’un panneau d’administration Django pour gérer les tâches (ajout, modification, suppression).

---

## Prérequis

- Python 3.8 ou supérieur  
- Django 3.x ou 4.x  
- Un environnement virtuel recommandé (venv, virtualenv, etc.)  
- Base de données SQLite (par défaut)

---

## Installation

1. **Cloner le projet**  
```bash
git clone <URL_DU_PROJET>
cd <NOM_DU_DOSSIER>

Installer les dépendances

pip install -r requirements.txt
 
 Créer un superutilisateur (pour accéder à l’admin Django)

python manage.py createsuperuser

Utilisation

    Accéder à la liste des tâches :
    http://127.0.0.1:8000/taches/

    Accéder à l’administration Django :
    http://127.0.0.1:8000/admin
    Se connecter avec le superutilisateur créé pour gérer les tâches.