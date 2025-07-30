 web_show

**web_show** est un package Django simple qui permet d’ajouter rapidement une page web dans votre projet.  
La page générée ne contient **aucun style CSS intégré**, ce qui vous permet de la personnaliser vous-même avec Tailwind CSS ou tout autre framework.

---

## 🚀 Installation


```bash
pip install web-show
```

## 🚀 Utilisation

```bash
pip install /chemin/vers/le/dossier/web_show

⚙️ Intégration dans un projet Django

1. Ajouter l'app dans INSTALLED_APPS
Dans votre fichier settings.py, ajoutez :

INSTALLED_APPS = [
    ...
    'web_show',
]


2. Ajouter les URLs dans urls.py
Dans le fichier urls.py de votre projet principal :

urlpatterns = [
    path('webshow/', include('web_show.urls')),
]

▶️ Lancement
Lancez le serveur Django :


python manage.py runserver
Puis visitez : http://127.0.0.1:8000/webshow/
