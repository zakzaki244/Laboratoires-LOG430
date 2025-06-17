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

--------------------
/////////////////////
------------------------
## Description 
Ce dépôt contient la nouvelle version de l’application POS (Point Of Sale), évoluant d’une architecture 2-tiers vers **une architecture 3-tiers** réalisée en Python et conteneurisée avec Docker :

- Client : interface utilisateur (Web)

- Serveur applicatif : logique métier Python (API REST Flask)

- Base de données : PostgreSQL, hébergée dans un conteneur dédié

---
##  1. Analyse et continuité 
***(aidé par Chatgpt pour savoir des precisions sur les outils les plus optimales pour le coté interface utilisateur)***

### a) Résumé des solutions Labs 0 et 1
Lab0 – Hello World : 
Le Lab0 posait les bases de la prise en main du workflow CI/CD, du dépôt GitHub et de la conteneurisation avec Docker.
L’objectif était simplement de :
- Créer un dépôt Git, un pipeline CI minimal et un Dockerfile
- Développer un script Python affichant “Hello World” en console
- S’assurer que l’application tourne correctement en local et dans un conteneur Docker

Lab1 – Application POS (Point of Sell) en CLI (ligne de commande console) : 
Le Lab1 constituait la première vraie application : Une caisse enregistreuse (POS) en architecture 2-tiers (client/serveur) :
- Interface console (CLI) : menu texte interactif permettant à l’utilisateur de rechercher des produits, enregistrer des ventes, consulter le stock, etc.
- Base de données PostgreSQL : stocke les produits, ventes et stocks de manière persistante
- SQLAlchemy (bibliothèque Python open source qui simplifie la manupulation de base de données SQL) (ORM) : relie le code Python à la base de données pour effectuer les opérations CRUD (création, lecture, mise à jour, suppression)

### b) Les éléments à conserver, modifier ou refactorer
**À conserver :**
Toute la logique métier (gestion des ventes, produits, stocks) ainsi que la couche d’accès aux données (service.py, dao.py, models.py, db.py) sont robustes et réutilisables pour le Lab2.

**À modifier :**
L’interface utilisateur doit être adaptée : on abandonne le menu console (CLI) pour une interface web plus conviviale via Flask et les templates HTML.

**À refactorer :**
Clarifier la séparation entre le contrôleur (gestion des routes Flask) et la logique métier, afin de préparer l’architecture 3-tiers.

### c) Nouvelles exigences et défis architecturaux 
- Passer d’une application 2-tiers (CLI + BD) à une architecture 3-tiers (Web + BD + Serveur Application) :
   -> Client : navigateur web (interface utilisateur)
   -> Serveur d’application : Flask (logique métier, gestion des requêtes, génération HTML)
   -> Base de données : PostgreSQL

- Gérer la navigation web : formulaires, sessions, gestion des erreurs utilisateur (par exemple : validation de saisie, messages d’erreur dynamiques)
- Maintenir la déployabilité : doit fonctionner via Docker Compose pour faciliter les tests et la reproductibilité

### d) Réflexion DDD (Domain-Driven Design) et identification des sous-domaines fonctionnels

Pour notre système de gestion de caisse (POS), une analyse DDD **Domain-Driven Design (DDD)** nous conduit à identifier plusieurs sous-domaines fonctionnels, chacun reflétant une partie du métier :

#### Sous-domaines identifiés pour le POS

- **Ventes en magasin** : gestion du panier, passage en caisse, historique des ventes.
- **Gestion logistique** : suivi des stocks, approvisionnement, mouvements d’inventaire.
- **Supervision par la maison mère** : génération de rapports, statistiques globales, suivi des performances du magasin.

> Chacun de ces sous-domaines pourra être traduit par des routes ou modules dédiés dans l’application web (ex : `/vente`, `/stock`, `/rapports`).

### Pourquoi DDD ?
- **Vocabulaire partagé** (« Ubiquitous Language ») entre développeurs et métier
- **Bounded contexts** : séparation claire des règles métier entre chaque sous-domaine
- **Entities/Services/Repositories** : architecture modulaire, testable et maintenable

Le DDD facilite la modularité, l’évolutivité et la robustesse du projet, tout en assurant un alignement fort entre besoins métier et code source.

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
   git checkout lab2

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
   pytest -q

## Installation Conteneurisation & orchestration 

1. **Docker Compose**  
   ```bash
   docker compose up --build
   et pour arrêter et supprimer les conteneurs :
   docker-compose down

## Pipeline CI/CD
À chaque push ou pull request sur main :
- Lint (flake8)
- Tests (pytest)
- Build & Push (Docker)

## Choix technologiques

| Composant        | Outil / Bibliothèque | Justification                                                                |
|------------------|----------------------|------------------------------------------------------------------------------|
| Langage          | Python 3.11          | Syntaxe claire, riche écosystème, portable                                   |
| Framework Web/API| Flask                | Léger, flexible, facile à déployer en REST, parfait pour prototyper          |
| ORM              | SQLAlchemy           | Abstraction SQL/objet, gestion des transactions, compatible PostgreSQL/SQLite |
| Base de données  | PostgreSQL           | ACID, fiable, conteneurisable, scalable                                      |
| Conteneurisation | Docker               | Isolation, reproductibilité, déploiement uniforme                            |
| Orchestration    | Docker Compose       | Lancement multi-conteneurs en une seule commande                             |
| Tests            | pytest               | Fixtures, plugins, large communauté                                          |
| CI/CD            | GitHub Actions       | Intégré au dépôt, workflows “lint → test → build → push” faciles à configurer|

## Explications techniques du code
- **main.py**(Flask) : serveur d’application, expose des routes (REST ou templates web)
- **static/** : ressources statiques (JS, CSS, images)
- **templates/** : fichiers HTML pour l’interface web
- **service.py** : logique métier, orchestration entre client web et base de données
- **dao.py** : accès brut à la BD, opérations CRUD sur les modèles
- **models.py** : définition des tables/entités métier
- **db.py** : configuration et connexion à la BD


## Structure
<pre>
Laboratoire-LOG430/
├── src/
│   └── app.py
│   └── main.py
│   └── service.py 
│   └── dao.py  
│   └── models.py 
│   └── db.py 
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── refund.html
│   │   ├── sale.html
│   │   ├── search.html
│   │   ├── stock.html
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── docs/
│   ├── ADR/
│   │   ├── ADR 0001.md
│   │   └── ADR 0002.md
├── tests/
│   └── test_connexion.py
│   └── test_dao.py  
├── .github/
│   └── workflows/
│       └── ci.yml
└── README.md
</pre>
