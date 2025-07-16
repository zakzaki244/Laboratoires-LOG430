# 9. Décisions d'Architecture (ADR)

## ADR 0001 - Architecture Microservices

**Status:** accepted

### Contexte
Le projet e-commerce nécessite une architecture scalable, maintenable et permettant le déploiement indépendant des différentes fonctionnalités (catalogue, panier, commandes, utilisateurs). L'équipe doit choisir entre une architecture monolithique et une architecture microservices.

### Décision
Adoption d'une architecture microservices avec les services suivants :
- customer-service (gestion utilisateurs)
- product-service (catalogue produits)
- cart-service (panier d'achat)
- checkout-service (processus de commande)
- sales-service (historique des ventes)
- store-service (gestion magasins)
- api-gateway (point d'entrée unifié)

### Justification
- **Scalabilité** : Chaque service peut être scalé indépendamment selon ses besoins
- **Maintenance** : Équipes peuvent travailler sur différents services en parallèle
- **Technologie** : Possibilité d'utiliser différentes technologies par service si nécessaire
- **Déploiement** : Déploiement indépendant des services
- **Résilience** : Panne d'un service n'affecte pas les autres

### Conséquences
- **Positives** :
  - Développement parallèle par équipes spécialisées
  - Scalabilité granulaire
  - Isolation des pannes
  - Flexibilité technologique
- **Négatives** :
  - Complexité de coordination entre services
  - Latence réseau entre services
  - Gestion des transactions distribuées
  - Complexité de monitoring et debugging

---

## ADR 0002 - Utilisation de Python/Flask

**Status:** accepted

### Contexte
Le choix du langage et du framework pour implémenter les microservices. Les options considérées incluent Python/Flask, Python/Django, Node.js/Express, et Java/Spring Boot.

### Décision
Utilisation de Python avec le framework Flask pour tous les microservices.

### Justification
- **Simplicité** : Flask est léger et permet une mise en place rapide
- **Flexibilité** : Architecture modulaire adaptée aux microservices
- **Écosystème** : Riche écosystème de librairies Python
- **Compétences** : Expertise de l'équipe en Python
- **Productivité** : Développement rapide et syntaxe claire

### Conséquences
- **Positives** :
  - Développement rapide et efficace
  - Code maintenable et lisible
  - Large communauté et support
  - Intégration facile avec bases de données
- **Négatives** :
  - Performance moindre que des langages compilés
  - GIL (Global Interpreter Lock) peut limiter le parallélisme
  - Dépendance à la version Python

---

## ADR 0003 - Authentification JWT

**Status:** accepted

### Contexte
Le système nécessite une authentification sécurisée et scalable pour les utilisateurs. Les options incluent les sessions serveur, les tokens JWT, et l'authentification OAuth externe.

### Décision
Implémentation d'une authentification basée sur les tokens JWT (JSON Web Tokens).

### Justification
- **Stateless** : Pas de stockage de session côté serveur
- **Scalabilité** : Tokens auto-contenus, pas de synchronisation entre instances
- **Sécurité** : Signature cryptographique des tokens
- **Flexibilité** : Support des rôles et permissions dans le token
- **Standards** : Standard ouvert largement adopté

### Conséquences
- **Positives** :
  - Scalabilité horizontale sans partage d'état
  - Réduction de la charge sur le serveur
  - Facilité d'intégration avec d'autres services
  - Gestion des rôles intégrée
- **Négatives** :
  - Impossibilité de révoquer un token avant expiration
  - Taille des tokens plus importante que les sessions
  - Complexité de gestion des tokens expirés

---

## ADR 0004 - Base de Données par Service

**Status:** accepted

### Contexte
Dans une architecture microservices, la question de la persistance des données est cruciale. Options : base de données partagée, base de données par service, ou mix des deux approches.

### Décision
Chaque microservice possède sa propre base de données SQLite en développement, avec migration possible vers PostgreSQL en production.

### Justification
- **Isolation** : Chaque service contrôle son schéma de données
- **Autonomie** : Pas de dépendance sur d'autres services pour les données
- **Scalabilité** : Possibilité d'optimiser chaque base pour son usage
- **Résilience** : Panne d'une base n'affecte pas les autres services

### Conséquences
- **Positives** :
  - Indépendance des équipes de développement
  - Possibilité d'optimiser chaque schéma
  - Isolation des pannes
  - Flexibilité dans le choix des technologies de stockage
- **Négatives** :
  - Complexité des requêtes cross-services
  - Gestion des transactions distribuées
  - Consistance éventuelle vs consistance forte
  - Duplication potentielle de données

---

## ADR 0005 - API Gateway Centralisée

**Status:** accepted

### Contexte
Avec plusieurs microservices, les clients doivent connaître les adresses de chaque service. Il faut une solution pour centraliser l'accès et gérer les préoccupations transversales.

### Décision
Implémentation d'une API Gateway centralisée gérant l'authentification, le routage, et la limitation de débit.

### Justification
- **Point d'entrée unique** : Simplification pour les clients
- **Sécurité centralisée** : Authentification et autorisation en un point
- **Monitoring unifié** : Logs et métriques centralisées
- **Gestion du trafic** : Rate limiting et load balancing

### Conséquences
- **Positives** :
  - Simplification de l'architecture client
  - Sécurité centralisée et cohérente
  - Monitoring et observabilité améliorés
  - Gestion uniforme des erreurs
- **Négatives** :
  - Point de défaillance unique potentiel
  - Latence additionnelle
  - Complexité de configuration
  - Risque de devenir un goulot d'étranglement

---

## ADR 0006 - Containerisation Docker

**Status:** accepted

### Contexte
Le déploiement et la gestion des microservices nécessitent une solution de packaging et d'orchestration. Les options incluent le déploiement traditionnel, Docker, et les solutions cloud natives.

### Décision
Utilisation de Docker pour containeriser chaque microservice avec Docker Compose pour l'orchestration locale.

### Justification
- **Portabilité** : Même environnement dev/test/prod
- **Isolation** : Chaque service dans son propre conteneur
- **Scalabilité** : Facilité de scaling horizontal
- **Déploiement** : Déploiement cohérent et reproductible

### Conséquences
- **Positives** :
  - Environnements cohérents
  - Déploiement simplifié
  - Isolation des dépendances
  - Facilité de scaling
- **Négatives** :
  - Courbe d'apprentissage Docker
  - Overhead de performance
  - Complexité de debugging
  - Gestion des volumes et réseaux

---

## ADR 0007 - Logging Structuré JSON

**Status:** accepted

### Contexte
Le monitoring et debugging d'une architecture microservices nécessite une stratégie de logging cohérente et analysable. Les options incluent les logs texte traditionnels et les logs structurés JSON.

### Décision
Implémentation d'un système de logging structuré au format JSON avec corrélation des traces entre services.

### Justification
- **Analysabilité** : Logs facilement parsables par les outils
- **Corrélation** : Trace ID pour suivre les requêtes cross-services
- **Standardisation** : Format uniforme pour tous les services
- **Observabilité** : Intégration avec les outils de monitoring

### Conséquences
- **Positives** :
  - Debugging facilité avec la corrélation
  - Intégration avec les outils d'analyse
  - Monitoring et alerting améliorés
  - Standardisation des logs
- **Négatives** :
  - Logs plus volumineux
  - Complexité de mise en place
  - Dépendance aux outils d'analyse
  - Coût de stockage plus élevé

---

## ADR 0008 - Communication Synchrone REST

**Status:** accepted

### Contexte
Les microservices doivent communiquer entre eux. Les options incluent REST synchrone, messaging asynchrone, et GraphQL.

### Décision
Utilisation de REST pour la communication synchrone entre services, avec possibilité d'ajouter du messaging asynchrone pour les événements.

### Justification
- **Simplicité** : REST est bien connu et documenté
- **Tooling** : Excellent support d'outils et librairies
- **Debugging** : Facilité de test et debugging
- **Standards** : Approche standardisée et largement adoptée

### Conséquences
- **Positives** :
  - Facilité de développement et test
  - Excellente documentation et tooling
  - Compatibilité avec les standards web
  - Courbe d'apprentissage faible
- **Négatives** :
  - Couplage temporel entre services
  - Gestion des pannes en cascade
  - Latence additionnelle
  - Complexité de gestion des timeouts

---

## ADR 0009 - Configuration Externalisée

**Status:** accepted

### Contexte
La configuration des microservices doit être flexible et adaptable selon les environnements (dev, test, prod). Les options incluent les fichiers de configuration, variables d'environnement, et configuration centralisée.

### Décision
Utilisation des variables d'environnement pour la configuration avec des valeurs par défaut et validation au démarrage.

### Justification
- **Flexibilité** : Configuration différente par environnement
- **Sécurité** : Pas de secrets dans le code
- **Déploiement** : Facilité de déploiement sans rebuild
- **Standards** : Approche 12-factor app

### Conséquences
- **Positives** :
  - Sécurité améliorée (pas de secrets hardcodés)
  - Flexibilité de déploiement
  - Respect des bonnes pratiques
  - Facilité de configuration par environnement
- **Négatives** :
  - Complexité de gestion des variables
  - Risque d'erreur de configuration
  - Debugging plus complexe
  - Dépendance à l'infrastructure de déploiement
