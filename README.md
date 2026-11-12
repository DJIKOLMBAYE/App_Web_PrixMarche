# PrixMarché

Application Django de gestion des marchés, produits, enquêteurs, affectations et
relevés de prix. Elle utilise SQLite et comprend un espace d’administration.

## Installation locale

Depuis le dossier contenant `manage.py` :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py test Enqueter
python manage.py runserver
```

Ouvrir ensuite `http://127.0.0.1:8000/`. Un compte créé depuis la page
d’inscription reçoit un profil enquêteur lié à son matricule. Les relevés sont
attribués côté serveur à ce profil ; leur auteur ne peut pas être choisi dans le
formulaire. Un administrateur peut également associer un compte à un enquêteur
dans l’interface d’administration.

## Administration des données

L’administration Django est accessible à `http://127.0.0.1:8000/admin/`.
Pour autoriser un compte administrateur, exécuter une fois la commande suivante
depuis le dossier contenant `manage.py`, puis choisir un nom d’utilisateur et un
mot de passe lorsque Django le demande :

```powershell
python manage.py createsuperuser
```

Connectez-vous ensuite à `/admin/`. Le lien **Administration** apparaît dans
le menu des pages lorsque vous êtes connecté à un compte administrateur. Les
comptes ordinaires ne peuvent pas accéder à cette interface; les pages de
gestion métier restent accessibles depuis le menu principal.

La migration `0002_complete_prixmarche` remplace le schéma initial de
l’application (notamment le modèle Région) par les cinq relations du TP. Elle
supprime les anciennes tables de l’application. Sauvegarder la base avant de
l’appliquer si elle contient des données à conserver.

## Configuration de production

Ne pas exposer `runserver` sur Internet. Sur un serveur Linux, installer les
dépendances puis définir les variables d’environnement avant de migrer :

```sh
export DJANGO_SECRET_KEY='une-cle-longue-et-confidentielle'
export DJANGO_DEBUG=0
export DJANGO_ALLOWED_HOSTS='prix.exemple.cm'
export DJANGO_SECURE_SSL_REDIRECT=1
export DJANGO_SECURE_HSTS_SECONDS=31536000
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
gunicorn prixmarche.wsgi:application --bind 127.0.0.1:8000
```

Lancer Gunicorn sous un service `systemd`, derrière Nginx configuré pour
terminer HTTPS et transmettre `X-Forwarded-Proto`. Nginx peut servir
`staticfiles/` directement. Garder `db.sqlite3` sur un stockage persistant,
restreindre ses permissions et tester régulièrement les sauvegardes et
restaurations.

En production, conserver `DEBUG=False`, fournir une liste `ALLOWED_HOSTS`
limitée aux domaines réellement utilisés et ne jamais versionner la clé Django,
la base SQLite ou le fichier `.env`.
