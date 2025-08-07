# 9. Décisions d'Architecture (ADR)

---

## ADR 001 - Choix du Pattern Saga Orchestrée vs Saga Chorégraphiée

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

## ADR 002 - Communication Synchrone vs Asynchrone pour la Saga

**Status:** accepted  
**Context:** Laboratoire 6 - Architecture de communication inter-services

### Contexte
L'orchestrateur Saga doit communiquer avec les microservices (product, sales, customer) pour exécuter les étapes de la transaction distribuée. Le choix du mode de communication impacte les performances, la fiabilité et la complexité d'infrastructure.

**Options considérées :**
1. **Communication synchrone** (HTTP REST)
2. **Communication asynchrone** (Messages via broker)
3. **Approche hybride** (sync pour lectures, async pour écritures)

### Décision
Adoption de la **communication synchrone HTTP REST** pour tous les appels inter-services de la Saga.

### Justification

**Avantages du synchrone :**
- ✅ **Simplicité d'infrastructure** : Pas de broker de messages à gérer (RabbitMQ/Kafka)
- ✅ **Cohérence immédiate** : Réponse directe des services avec statut de l'opération
- ✅ **Debugging facilité** : Traces directes dans les logs, call stack claire
- ✅ **Gestion d'erreurs standard** : Codes HTTP pour succès/échecs
- ✅ **Tests simplifiés** : Pas de mocking de queues/topics
- ✅ **Développement rapide** : APIs REST déjà disponibles dans les microservices

**Inconvénients assumés :**
- ❌ **Latence plus élevée** : Attente des réponses à chaque étape
- ❌ **Disponibilité couplée** : Échec si service cible indisponible
- ❌ **Scalabilité limitée** : Moins performant sous très forte charge
- ❌ **Timeouts nécessaires** : Gestion des services lents

### Alternatives Considérées

1. **Messages asynchrones (Event-driven)**
   - Rejetée car complexité infrastructure trop importante pour le laboratoire
   - Nécessiterait RabbitMQ/Kafka + gestion des Dead Letter Queues
   - Difficulté de corrélation des événements

2. **Approche hybride (sync + async)**
   - Rejetée car complexité de développement
   - Difficile de tester et maintenir

### Conséquences

**Positives :**
- Infrastructure Docker simplifiée (pas de broker de messages)
- Développement et déploiement rapides
- Debugging direct avec curl/Postman
- Logs de requêtes HTTP tracés facilement

**Négatives :**
- Timeouts et retry patterns nécessaires
- Circuit breakers recommandés pour la production
- Monitoring de la latence end-to-end critique

**Stratégies de mitigation :**
- Timeouts configurés sur tous les appels (30s max)
- Retry automatique avec backoff exponentiel (3 tentatives)
- Health checks sur tous les services
- Métriques de latence dans Prometheus

### Configuration Technique

```python
# Timeouts et retry dans l'orchestrateur
TIMEOUT_CONFIG = {
    "connect_timeout": 5,    # 5s pour établir la connexion
    "read_timeout": 30,      # 30s pour recevoir la réponse
    "max_retries": 3,        # 3 tentatives maximum
    "backoff_factor": 1      # 1s, 2s, 4s entre tentatives
}
```

