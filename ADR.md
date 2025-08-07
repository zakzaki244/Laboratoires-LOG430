# Architecture Decision Records (ADR) - Lab 7

---

## ADR 001 - Choix de Redis Streams vs Apache Kafka pour le Pub/Sub

**Status:** accepted  
**Context:** Lab 7 - Architecture Événementielle avec Pub/Sub

### Contexte
Pour implémenter l'architecture événementielle du Lab 7, nous devions choisir une solution de message broker pour le pattern Pub/Sub. Les principales options évaluées étaient :

1. **Redis Streams** : Solution légère basée sur Redis
2. **Apache Kafka** : Plateforme de streaming distribuée
3. **RabbitMQ** : Message broker traditionnel AMQP

### Décision
Adoption de **Redis Streams** comme solution de Pub/Sub pour le Lab 7.

### Justification

**Avantages Redis Streams :**
- ✅ **Simplicité de déploiement** : Une seule instance Redis suffit
- ✅ **Performance** : Latence très faible (< 1ms) pour le lab
- ✅ **Persistance** : Messages persistés sur disque automatiquement
- ✅ **Groupes de consommateurs** : Support natif pour distribution des messages
- ✅ **Atomic operations** : Garanties ACID sur les opérations
- ✅ **Compatibilité** : S'intègre facilement avec l'écosystème Redis existant
- ✅ **Ressources** : Consommation mémoire et CPU réduite
- ✅ **Développement rapide** : API simple pour le prototypage

**Inconvénients :**
- ❌ **Scalabilité limitée** : Moins adapté pour des millions de messages/seconde
- ❌ **Écosystème** : Moins d'outils tiers que Kafka
- ❌ **Durabilité** : Moins de garanties de durabilité que Kafka

### Alternatives Considérées

1. **Apache Kafka**
   - Rejeté car complexité excessive pour un laboratoire 
   - Nécessite Zookeeper et configuration cluster
   - Overhead de ressources important pour les volumes du lab

2. **RabbitMQ**
   - Rejeté car modèle plus orienté queues traditionnelles
   - Moins adapté au streaming d'événements en temps réel

### Conséquences

**Positives :**
- Déploiement simplifié avec Docker Compose
- Performance excellente pour les besoins du lab
- Code plus simple à comprendre et maintenir
- Tests plus rapides à exécuter

**Négatives :**
- Solution moins "production-ready" pour grandes échelles
- Expertise Redis requise plutôt que Kafka (standard industrie)

---

## ADR 002 - Choix de MongoDB vs PostgreSQL pour l'Event Store

**Status:** accepted  
**Context:** Lab 7 - Implémentation Event Sourcing avec Event Store

### Contexte
L'implémentation d'Event Sourcing nécessite un Event Store pour persister tous les événements du système. Nous avions le choix entre :

1. **MongoDB** : Base NoSQL orientée documents
2. **PostgreSQL** : Base relationnelle avec support JSON
3. **EventStore DB** : Base spécialisée pour Event Sourcing

### Décision
Adoption de **MongoDB** comme Event Store pour le Lab 7.

### Justification

**Avantages MongoDB :**
- ✅ **Structure naturelle** : Documents JSON parfaits pour les événements
- ✅ **Schéma flexible** : Évolution des événements sans migration
- ✅ **Performance** : Insertions très rapides pour append-only workload
- ✅ **Requêtes riches** : Agrégations complexes pour projections CQRS
- ✅ **Indexation** : Index sur timestamp, type d'événement, aggregate_id
- ✅ **Sharding** : Scalabilité horizontale native
- ✅ **Compression** : Stockage efficace des événements JSON
- ✅ **Change Streams** : Notifications temps réel des changements

**Inconvénients :**
- ❌ **Consistance** : Eventual consistency par défaut
- ❌ **Transactions** : Support limité des transactions ACID
- ❌ **Expertise** : Courbe d'apprentissage pour l'équipe

### Alternatives Considérées

1. **PostgreSQL avec JSONB**
   - Rejeté car less natural pour documents nested JSON
   - Performance moindre pour append-only workloads
   - Complexité des requêtes d'agrégation

2. **EventStore DB**
   - Rejeté car spécialisé mais overhead pour un laboratoire
   - Moins de documentation et d'exemples
   - Compétences spécifiques requises

### Conséquences

**Positives :**
- Modèle de données très naturel pour les événements
- Performance excellente pour les insertions et lectures
- Projections CQRS facilitées par le pipeline d'agrégation
- Intégration simple avec les services Python/Flask

**Négatives :**
- Gestion de la cohérence plus complexe
- Backup et recovery différents des bases relationnelles

---

## ADR 003 - Choix du Pattern Saga Orchestrée vs Saga Chorégraphiée (Lab 6)

**Status:** accepted (Lab 6) → superseded (Lab 7)  
**Context:** Évolution du Lab 6 vers Lab 7

**Status:** accepted  
**Context:** Laboratoire 6 - Saga pour transactions distribuées

### Contexte
Pour gérer les transactions distribuées dans l'architecture microservices e-commerce, nous devions choisir entre deux patterns principaux pour assurer la cohérence des données :

1. **Saga Orchestrée** : Coordination centralisée via un orchestrateur dédié
2. **Saga Chorégraphiée** : Coordination décentralisée via événements inter-services

Le choix impact directement la complexité, la maintenabilité et l'observabilité du système.

### Décision
Adoption du **Pattern Saga Orchestrée** avec orchestrateur centralisé synchrone pour la gestion des commandes e-commerce.

### Justification

**Avantages de l'orchestration :**
- ✅ **Contrôle centralisé** : Toute la logique métier est dans un seul service
- ✅ **Observabilité** : Point unique pour monitoring, debugging et métriques
- ✅ **Cohérence** : Gestion séquentielle des étapes, plus prévisible
- ✅ **Simplicité de développement** : Plus facile à comprendre et maintenir
- ✅ **Gestion d'erreurs centralisée** : Compensation et rollback dans un seul endroit
- ✅ **Tests plus simples** : Scénarios d'échec centralisés

**Inconvénients :**
- ❌ **Point de défaillance unique** : L'orchestrateur devient critique
- ❌ **Couplage** : Les services connaissent l'existence de l'orchestrateur  
- ❌ **Latence** : Communication synchrone potentiellement plus lente
- ❌ **Scalabilité** : Goulot d'étranglement potentiel sous forte charge

### Alternatives Considérées

1. **Saga Chorégraphiée** 
   - Rejetée car plus complexe à debugger et tracer
   - Logique métier dispersée dans plusieurs services
   - Difficulté de visualisation du flux global

### Conséquences

**Positives :**
- Développement plus rapide du laboratoire
- Debugging et troubleshooting facilités
- Métriques et logs centralisés
- Tests d'intégration simplifiés

**Négatives :**
- Surveillance accrue de la disponibilité de l'orchestrateur nécessaire
- Besoin de mécanismes de failover pour la production

**Stratégies de mitigation :**
- Monitoring renforcé avec alertes sur l'orchestrateur
- Health checks et circuit breakers
- Réplication future de l'orchestrateur pour la haute disponibilité
---