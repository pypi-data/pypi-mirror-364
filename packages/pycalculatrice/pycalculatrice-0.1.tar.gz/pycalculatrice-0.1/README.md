# PyCalculatrice

Une simple application Django qui fournit une calculatrice web basique avec les opérations addition, soustraction, multiplication et division.

---

## Installation

### 1. Cloner le dépôt (ou télécharger le package)

```bash
git clone https://ton-repo-ou-chemin/pycalculatrice.git
cd pycalculatrice

2. Créer et activer un environnement virtuel (optionnel mais recommandé)

python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3. Installer les dépendances

pip install -r requirements.txt

4. Installer le package localement (mode editable)

pip install -e .

Utilisation dans un projet Django
1. Créer un projet Django (si ce n'est pas déjà fait)

django-admin startproject monprojet
cd monprojet

2. Ajouter pycalculatrice dans INSTALLED_APPS dans monprojet/settings.py

INSTALLED_APPS = [
    # autres apps
    'pycalculatrice',
]

3. Inclure les URLs dans monprojet/urls.py

from django.urls import path, include

urlpatterns = [
    # autres urls
    path('calculatrice/', include('pycalculatrice.urls')),
]

4. Appliquer les migrations Django

python manage.py migrate

5. Lancer le serveur

python manage.py runserver
