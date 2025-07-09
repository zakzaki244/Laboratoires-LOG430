# Lab4-LOG430 – Test de charge et Observabilite

[![CI](https://github.com/zakzaki244/Lab0-LOG430/actions/workflows/ci.yml/badge.svg)](https://github.com/zakzaki244/Lab0-LOG430/actions)

Dans ce laboratoire j'ai effectué la correction des remarques du professeur Fabio et implémenter les fonctionnalitées correctement !

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

---

## 2. Test de charge initial avec K6

Un test de charge est réalisé avec l’outil K6 pour simuler une montée en charge et observer les métriques suivantes : les 4 Golden Signals

- Latence (p95 / p99) : temps de reponse moyen
- Trafic/Requêtes par seconde
- Saturation : utilisation charge CPU / Mémoire, threads, pool de connexions.
-  Erreurs : taux de réponses HTTP 4xx ou 5xx.

### 🔍 Tableau de bord Grafana
Des dashboards Grafana sont utilisés pour visualiser les résultats du test :

- **Latence** (95e et 99e percentile) : ![latence](./docs/Tableaudebordinitial1.png)
- **Requêtes par seconde** : ![rps](./docs/requeteparsecondeinitial.png)
- **Utilisation CPU & RAM** : ![cpu_ram](./docs/RAMinitial.png)
- **Fichiers ouverts** : ![fds](./docs/Saturationinitial.png) ![fds](./docs/httperreur.png)

> Les graphiques qui ne présentent pas de data c'est parcequ'il n'y a pas de données d'erreur. 

### Explication des axes sur les graphes Grafana :

- **Axe des abscisses (horizontal)** : Temps (en heures:minutes)
- **Axe des ordonnées (vertical)** :
  - Pour la latence : temps de réponse en secondes
  - Pour la charge CPU : pourcentage d’utilisation (de 0 à 1 = 0% à 100%)
  - Pour la mémoire : en octets
  - Pour les requêtes par seconde : nombre de requêtes traitées par seconde

---

## 3. Résultats des tests de charge (K6 + Grafana)

### Scénario 1 — Infrastructure de base (sans cache, sans load balancer)
Objectif : Évaluer les performances de l'application dans sa version initiale.

### Scénario 2 — Ajout du cache (Redis)
Objectif : Réduire les accès fréquents à la base de données et améliorer la latence.

### Scénario 3 — Ajout du Load Balancer
Objectif : Répartir la charge entre plusieurs instances de l’application.

## 4. Prochaines étapes

- Mise en place du cache avec Redis
- Ajout d’un Load Balancer (via Nginx ou autre)
- 
- Comparaison des résultats de test de charge :
  - avant optimisation (baseline)
  - après ajout du cache
  - après ajout du load balancing

Chaque étape sera documentée avec captures Grafana et analyse.

---

## 5. Objectifs pédagogiques

- Utiliser un outil de test de charge (K6)
- Observer les métriques d’un système web via Prometheus + Grafana
- Identifier les goulots d’étranglement
- Implémenter des solutions d’amélioration (cache, équilibrage de charge)
- Évaluer l’impact sur les performances

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
