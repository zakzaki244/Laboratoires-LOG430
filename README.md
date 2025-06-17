# Lab3-LOG430 – Exposition d’une API RESTful 

[![CI](https://github.com/zakzaki244/Lab0-LOG430/actions/workflows/ci.yml/badge.svg)](https://github.com/zakzaki244/Lab0-LOG430/actions)

## 1. Architecture du projet

Le projet suit le principe MVC/hexagonal :
- `models.py` : Définition des modèles ORM SQLAlchemy (Store, Product, Sale…)
- `dao.py` : Accès bas niveau à la base de données (CRUD)
- `service.py` : Logique métier indépendante des routes (gestion ventes, stock…)
- `app.py` / `routes.py` : Contrôleurs, définition des routes Flask (Web et API REST)
- `db.py` : Configuration SQLAlchemy et connexion base
- `init_db.py` : Script d’initialisation/démo de la BDD

## 2. API REST

Une couche d’API REST a été ajoutée :  
Toutes les routes REST sont sous le préfixe `/api/` (voir `routes.py`).  
Exemples :
- `GET /api/products` : Retourne la liste de tous les produits au format JSON
- `GET /api/products/<id>` : Retourne un produit précis
- `POST /api/products` : Crée un produit (reçoit un JSON)


## 3. Structure claire des routes REST

- Toutes les routes REST sont clairement organisées sous `/api/` selon les entités (produit, magasin, vente).
- Exemples de routes :
    - `/api/products`
    - `/api/magasins`
    - `/api/ventes`
- Les méthodes HTTP utilisées sont conformes aux standards REST : `GET`, `POST`, `PUT`, `DELETE`.

## Endpoints REST disponibles

- `GET /api/products` : Liste de tous les produits
- `GET /api/products/<id>` : Détail d’un produit
- `POST /api/products` : Créer un produit (JSON attendu)
- `PUT /api/products/<id>` : Modifier un produit
- `DELETE /api/products/<id>` : Supprimer un produit

- `GET /api/magasins` : Liste des magasins
- `GET /api/magasins/<id>` : Détail d’un magasin (avec ses produits)
- `GET /api/ventes` : Liste des ventes

test :
 http://10.194.32.174:5000/api/magasins 

 http://10.194.32.174:5000/api/products

etc...

**Toutes les réponses sont au format JSON.**


## Documentation de l’API REST (Swagger / OpenAPI)

### Description

L’API REST du projet permet d’effectuer toutes les opérations principales sur les magasins, produits, et ventes.  
La documentation complète au format OpenAPI (Swagger) est générée automatiquement grâce à Flasgger.

### Accéder à la documentation Swagger UI

Après avoir démarré l’application (`docker compose up --build`), rendez-vous sur :

- [http://10.194.32.174:5000/apidocs/#/](http://10.194.32.174:5000/apidocs/#/)

Vous y trouverez :
- La liste de tous les endpoints (magasins, produits, ventes)
- Les méthodes HTTP disponibles (GET, POST, PUT, DELETE, PATCH…)
- Les paramètres d’entrée et de sortie
- Des exemples de requêtes/réponses
- La possibilité de tester l’API directement via l’interface

### Exemples de requêtes

- `GET /api/products` — Récupérer la liste des produits
- `POST /api/products` — Créer un produit (avec body JSON)
- `GET /api/ventes` — Voir toutes les ventes

### Standards

- Toutes les routes suivent les conventions REST (`/api/resource`, `/api/resource/id`)
- Les statuts de réponse HTTP sont respectés (200, 201, 404…)
- Les formats d’entrée/sortie sont en JSON

![Swagger API documentation](docs/ADR/API.png)


## Sécurité et accessibilité

- **CORS** activé pour permettre l’accès distant à l’API.
- **Authentification** : Toutes les requêtes POST/PUT/PATCH/DELETE exigent le header HTTP :
    Authorization: Bearer Supermarcher22102002

## Authentification & Sécurité API

Certaines routes de l’API REST nécessitent une authentification par token (type Bearer token).

### ➡️ Tester les endpoints sécurisés depuis Swagger

1. Rendez-vous sur l’interface Swagger UI ([[http://10.194.32.174:5000/apidocs](http://10.194.32.174:5000/apidocs)]).
2. Cliquez sur le bouton **“Authorize”** (icône de cadenas).
3. Entrez le token suivant :

    ```
    Bearer Supermarcher22102002
    ```

   (Ne pas mettre le mot "Bearer", il sera ajouté automatiquement.)

4. Les endpoints sécurisés peuvent désormais être testés via Swagger.

### ⚙️ Comment le token est-il validé ?

- À chaque requête, le serveur vérifie la présence de ce token dans l’en-tête HTTP :

    ```
    Authorization: Bearer supersecrettoken123
    ```
![Swagger API documentation](docs/ADR/TestAPIgetmagasinavecAuthorization.png)






- Si le token est absent ou incorrect, la réponse est 401 Unauthorized.
![Swagger API documentation](docs/ADR/TestAPIgetmagasinsansAuthorization.png)

##  Tests et Validation

- **Tests unitaires automatisés** :  
  Les endpoints REST de l’API sont testés avec `pytest` (voir `tests/test_api.py`).
- **Lancer les tests** :  
   ```bash
   pytest tests/
**Sécurité** :  
Tous les tests incluent l’en-tête d’authentification requis.
- **Swagger UI** :  
Tous les endpoints sont interactifs/testables depuis [Swagger UI](http://10.194.32.174:5000/apidocs).
- **CI/CD** :  
Les tests sont automatiquement exécutés à chaque push via GitHub Actions.


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
   git checkout lab3

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
