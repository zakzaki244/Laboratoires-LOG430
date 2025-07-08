# Lab4-LOG430 – Test de charge et Observabilite

[![CI](https://github.com/zakzaki244/Lab0-LOG430/actions/workflows/ci.yml/badge.svg)](https://github.com/zakzaki244/Lab0-LOG430/actions)

## 1. Architecture du projet

Le projet suit :
- `app.py` : 
  - Role : Point d’entrée Flask
    - enregistre les blueprints, configure Swagger, etc.
    - Iniitialise l’application Flask, 
    - Configure Swagger (documentation API), 
    - Enregistre les différents blueprints (web pour l’interface web, api pour l’API REST), 
    - Peut gérer la configuration globale, le CORS, les middlewares globaux, etc.
- `routes.py` : Routes API REST, Blueprint nommé api
  -  Role : Définit les routes REST API, utilisées par des clients externes ou du JavaScript front-end
     -  Utilise un Blueprint nommé api.
     -  Toutes les routes sont en /api/... (ex : /api/products, /api/ventes, etc.).
     -  Réponses toujours en JSON.
     -  Sécurisation possible via token.
     -  Contient des docstrings Swagger pour la documentation automatique.
- `web_routes.py` : Routes classiques pour le web (login, gestion HTML, ...), Blueprint nommé web
  - Role : Définit les routes classiques web (HTML), destinées à être utilisées par les utilisateurs via le navigateur.
    - Utilise un Blueprint nommé web.
    - Gère la connexion, l’affichage des pages HTML, les formulaires, etc
    - Retourne des templates HTML (ex : render_template("index.html", ...)).
    - Peut utiliser la session Flask pour l’authentification utilisateur.
    - Routage classique (ex : /login, /logout, /magasins, /products...).
- `src/db` : db.py / init_db.py
  - Role : Gestion de la base de données SQLAlchemy.
    - `db.py`: Définit la session, la connexion, le moteur, etc.
    - `init_db.py`: Script d’initialisation (création des tables, population de données...).
- `src/models/` : models.py, product.py, sale.py, store.py, etc.
  - Role : Définition des classes modèles ORM (SQLAlchemy) pour représenter les entités de la base (Product, Store, Sale, etc.).
- `src/services/` : product_service.py, sale_service.py, store_service.py, etc.
  - Role : Contient la logique métier (business logic) et les fonctions/services manipulant les entités (ex : création d’un produit, vente, remboursement, etc.). Elle sert d’interface entre les routes et les modèles. Elle permet de garder les routes propres et de factoriser le code métier.
- `src/templates/` : Fichiers HTML (Jinja2). Ce sont tous tes templates pour l’affichage côté utilisateur.

**Voici la difference entre les deux routes :**
web_routes.py permet aux utilisateurs d’utiliser le système dans un navigateur web. Mais routes.py sert à exposer les données et opérations pour des machines ou autres systèmes. Ainsi, le but principal de routes.py = rendre ton backend réutilisable et ouvert


##  Instructions
## Prérequis
- Python 3.11  
- Docker & Docker Compose  
- (Optionnel) `venv` ou `virtualenv` pour isoler l’environnement Python  

## Installation locale et exécution

1. **Cloner le projet**  
   ```bash
   git clone https://github.com/zakzaki244/Laboratoires-LOG430.git
   cd Laboratoires-LOG430
   git checkout lab4

2. **Environnement Python**
   Optionnel : créer et activer un environnement virtuel
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate et/ou sur Windows : venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   
4. **Lancer l'application interface web**  
   ```bash
   Ouvre le navigateur à l’adresse : http://10.194.32.174:5000/

5. **Tests unitaires**  
   ```bash
   pytest tests/

## Installation Conteneurisation & orchestration 

1. **Docker Compose**  
   ```bash
   docker compose up --build
   et pour arrêter et supprimer les conteneurs :
   docker-compose down
