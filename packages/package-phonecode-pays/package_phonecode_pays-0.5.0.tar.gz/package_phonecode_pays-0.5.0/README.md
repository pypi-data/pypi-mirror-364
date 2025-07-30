# package_phonecode_pays

`package_phonecode_pays` est un package Django qui permet d'obtenir l'indicatif téléphonique d'un pays en saisissant son nom.  
Il inclut une vue et un formulaire prêts à être utilisés dans n'importe quel projet Django.

---

## Fonctionnalités
- Formulaire permettant de saisir un pays.
- Retourne l’indicatif téléphonique correspondant.
- Facile à intégrer dans tout projet Django via `INSTALLED_APPS`.

---

## Installation

### Installer le package
Si tu as le package en local :
```bash
pip install package-phonecode-pays


Dans settings.py de ton projet Django :

INSTALLED_APPS = [
    ...
    'package_phonecode_pays',
]

Dans le urls.py principal de ton projet :

from django.urls import path, include

urlpatterns = [
    ...
    path('', include('package_phonecode_pays.urls')),
]
    Lance ton serveur Django :

python manage.py runserver

    Ouvre dans le navigateur :

http://127.0.0.1:8000/phonecode/
