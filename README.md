# 🏗️ Laboratoire 6 LOG430 - Saga Orchestrée Synchrone

## 📋 Vue d'ensemble

Ce laboratoire implémente une **Saga orchestrée synchrone** pour gérer le processus de commande dans une architecture microservices e-commerce. Le système assure la cohérence des données distribuées avec une gestion complète des échecs, des compensations automatiques et une observabilité avancée.

## 🎯 Objectifs du Laboratoire

1. **Saga orchestrée synchrone** : Coordination centralisée des microservices
2. **Machine d'état** : Suivi précis de l'évolution des commandes
3. **Gestion des échecs** : Mécanismes de compensation automatiques et rollback
4. **Observabilité** : Métriques Prometheus, dashboards Grafana et logs structurés
5. **Tests complets** : Validation des scénarios de succès et d'échec

---

#  RAPPORT STRUCTURÉ - LABORATOIRE 6

## 1. 🎭 Scénario Métier Implémenté

### Contexte
L'application e-commerce gère des commandes clients impliquant plusieurs microservices. Le défi principal est d'assurer la **cohérence des données distribuées** lors du processus de commande.

### Scénario Principal : "Commande Client"
1. **Acteur** : Client connecté
2. **Objectif** : Passer une commande de produits
3. **Préconditions** : 
   - Client authentifié
   - Produits disponibles dans le catalogue
   - Système de paiement opérationnel

### Flux Nominal
```
Client → [API Gateway] → [Saga Orchestrator]
                              ↓
                    ┌─── Product Service (Vérif. stock)
                    ├─── Product Service (Réservation)
                    ├─── Sales Service (Paiement)
                    └─── Sales Service (Confirmation)
```

### Défis Métier Résolus
- **Cohérence** : Éviter les commandes sans stock suffisant
- **Fiabilité** : Gérer les pannes de services
- **Traçabilité** : Suivre l'état de chaque commande
- **Compensation** : Annuler les opérations partielles en cas d'échec

### 📊 Diagramme de la Machine d'État

![Diagramme Machine d'État Saga](./Diagrammes-lab6/machineetat.png)

**États principaux :**
- `CREATED` : Commande initiée
- `STOCK_VERIFIED` : Vérification du stock réussie
- `STOCK_RESERVED` : Réservation du stock confirmée  
- `PAYMENT_PROCESSED` : Paiement traité avec succès
- `COMPLETED` : Commande finalisée (état final de succès)
- `FAILED` : Échec avec compensation (état final d'échec)

**Transitions critiques :**
- Chaque échec déclenche les compensations appropriées
- Les états sont persistés en base de données
- Traçabilité complète via les logs de saga


## 2. 🔄 Saga Implémentée : Orchestration Synchrone

### Architecture Choisie
**Pattern Saga Orchestrée** avec orchestrateur centralisé synchrone.

### Justification du Choix
- ✅ **Contrôle centralisé** : Plus facile à déboguer et monitorer
- ✅ **Cohérence** : Gestion séquentielle des étapes
- ✅ **Simplicité** : Logique métier centralisée
- ✅ **Observabilité** : Point unique de supervision

### Services Coordonnés
1. **Product Service** : Gestion des stocks
2. **Sales Service** : Traitement des paiements et ventes
3. **Customer Service** : Validation des clients (implicite)


### États et Transitions

| État | Description | Actions possibles |
|------|-------------|-------------------|
| `INITIATED` | Saga démarrée | → `STOCK_CHECKED`, `FAILED` |
| `STOCK_CHECKED` | Stock vérifié | → `STOCK_RESERVED`, `FAILED` |
| `STOCK_RESERVED` | Stock réservé | → `PAYMENT_PROCESSED`, `CANCELLED` |
| `PAYMENT_PROCESSED` | Paiement effectué | → `CONFIRMED`, `CANCELLED` |
| `CONFIRMED` | ✅ Succès final | Aucune (terminal) |
| `CANCELLED` | ❌ Annulé avec compensation | Aucune (terminal) |
| `FAILED` | ❌ Échec sans compensation | Aucune (terminal) |

## � Instructions de Déploiement et Tests

### Prérequis

- **Docker** (v20.10+) et **Docker Compose** (v2.0+)
- **Python** 3.11+
- **Git** pour cloner le projet
- **cURL** ou **Postman** pour les tests API

### 📦 Déploiement Complet

```bash
# 1. Cloner le projet (branche lab6)
git clone https://github.com/zakzaki244/Laboratoires-LOG430.git -b lab6
cd Laboratoires-LOG430

# 2. Vérifier les fichiers de configuration
ls -la docker-compose.yml

# 3. Démarrer toute l'infrastructure (base de données, services, monitoring)
docker-compose up -d

# 4. Vérifier que tous les services sont démarrés
docker-compose ps

# 5. Attendre que les services soient prêts (environ 30 secondes)
sleep 30

# 6. Initialiser les données de test
python init_all_data.py

# 7. Vérifier les logs du saga orchestrator
docker-compose logs saga-orchestrator
```

### 🔍 Vérification du Déploiement

```bash
# Vérifier l'état de tous les services
docker-compose ps

# Tester la connectivité des services
curl http://localhost:8080/health          # API Gateway
curl http://localhost:5001/health          # Product Service
curl http://localhost:5005/health          # Sales Service
curl http://localhost:5006/health          # Saga Orchestrator

# Vérifier les métriques Prometheus
curl http://localhost:9090/metrics         # Prometheus
curl http://localhost:5006/metrics         # Métriques Saga

# Accéder aux interfaces
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
# - Application: http://localhost:8080
```

### ⚡ Tests Rapides

#### Test de Succès
```bash
# Créer une commande qui réussit
curl -X POST http://localhost:5006/api/saga/order \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "1",
    "items": [
      {
        "product_id": 1,
        "quantity": 1,
        "price": 29.99
      }
    ]
  }'
```

#### Test d'Échec (Stock insuffisant)
```bash
# Commande avec quantité excessive
curl -X POST http://localhost:5006/api/saga/order \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "1",
    "items": [
      {
        "product_id": 1,
        "quantity": 999,
        "price": 29.99
      }
    ]
  }'
```

### 🧪 Suite de Tests Complète

```bash
# Naviguer vers le dossier des tests
cd saga-orchestrator/tests

# Exécuter tous les tests
python -m pytest test_saga.py -v

# Tests spécifiques
python test_saga_success.py      # Tests de succès
python test_saga_failure.py      # Tests d'échec
python test_compensation.py      # Tests de compensation
```

## 📡 API Endpoints

### 1. Créer une Saga de commande

```http
POST /api/saga/order
Content-Type: application/json

{
  "customer_id": "1",
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "price": 29.99
    }
  ]
}
```

**Réponse de succès :**
```json
{
  "success": true,
  "order_id": "uuid-12345",
  "state": "confirmed",
  "message": "Commande confirmée avec succès"
}
```

**Réponse d'échec :**
```json
{
  "success": false,
  "order_id": "uuid-12345",
  "state": "failed",
  "error": "Stock insuffisant pour certains produits"
}
```

### 2. Obtenir le statut d'une Saga

```http
GET /api/saga/{order_id}/status
```

**Réponse :**
```json
{
  "order_id": "uuid-12345",
  "customer_id": "1",
  "items": [...],
  "current_state": "confirmed",
  "created_at": "2025-07-16T18:00:00Z",
  "updated_at": "2025-07-16T18:00:05Z",
  "events": [
    {
      "event": "saga_started",
      "timestamp": "2025-07-16T18:00:00Z",
      "state": "initiated",
      "data": {"order_id": "uuid-12345"}
    }
  ],
  "error_message": null,
  "compensation_data": {...}
}
```


## 🧪 Tests

### Tests de succès

```bash
cd saga-orchestrator/tests
python test_saga_success.py
```

### Tests d'échec

```bash
python test_saga_failure.py
```

### Tests de compensation

```bash
python test_compensation.py
```

---

# 🔧 DOCUMENTATION TECHNIQUE

## � API Endpoints Détaillés

### 1. Créer une Saga de Commande

```http
POST /api/saga/order
Content-Type: application/json
```

**Payload :**
```json
{
  "customer_id": "1",
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "price": 29.99
    },
    {
      "product_id": 2,
      "quantity": 1,
      "price": 49.99
    }
  ]
}
```

**Réponse de Succès (201) :**
```json
{
  "success": true,
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "confirmed",
  "message": "Commande confirmée avec succès",
  "total_amount": 109.97,
  "processing_time_ms": 1245
}
```

**Réponse d'Échec (400/500) :**
```json
{
  "success": false,
  "order_id": "550e8400-e29b-41d4-a716-446655440001",
  "state": "failed",
  "error": "Stock insuffisant pour le produit 1",
  "details": {
    "step": "stock_check",
    "product_id": 1,
    "requested_quantity": 999,
    "available_quantity": 10
  }
}
```

### 2. Obtenir le Statut Détaillé d'une Saga

```http
GET /api/saga/{order_id}/status
```

**Réponse :**
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": "1",
  "items": [
    {"product_id": 1, "quantity": 2, "price": 29.99}
  ],
  "current_state": "confirmed",
  "created_at": "2024-07-16T18:00:00.000Z",
  "updated_at": "2024-07-16T18:00:05.245Z",
  "processing_time_ms": 5245,
  "events": [
    {
      "event": "saga_started",
      "timestamp": "2024-07-16T18:00:00.000Z",
      "state": "initiated",
      "data": {"order_id": "550e8400-e29b-41d4-a716-446655440000"}
    },
    {
      "event": "stock_check_success",
      "timestamp": "2024-07-16T18:00:01.123Z",
      "state": "stock_checked",
      "data": {"products_verified": 1}
    },
    {
      "event": "stock_reservation_success",
      "timestamp": "2024-07-16T18:00:02.456Z",
      "state": "stock_reserved",
      "data": {"products_reserved": 1}
    },
    {
      "event": "payment_success",
      "timestamp": "2024-07-16T18:00:04.789Z",
      "state": "payment_processed",
      "data": {"amount": 59.98}
    },
    {
      "event": "order_confirmed",
      "timestamp": "2024-07-16T18:00:05.245Z",
      "state": "confirmed",
      "data": {"sale_id": "sale-uuid-67890"}
    }
  ],
  "error_message": null,
  "compensation_data": {}
}
```

### 3. Déclencher Compensation Manuelle

```http
POST /api/saga/{order_id}/compensate
Authorization: Bearer {admin_token}
```

**Réponse :**
```json
{
  "success": true,
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "compensations_executed": [
    {
      "service": "product-service",
      "action": "stock_release",
      "status": "success",
      "details": {"products_released": 2}
    },
    {
      "service": "sales-service", 
      "action": "payment_refund",
      "status": "success",
      "details": {"refund_amount": 59.98}
    }
  ]
}
```


## ⚙️ Configuration Avancée

### Variables d'Environnement

```env
# Base de données
DATABASE_URL=postgresql://log430:laboratoire@saga-db:5432/sagadb

# Sécurité
SECRET_KEY=saga_secret_key_super_secure
JWT_SECRET_KEY=jwt_secret_key_for_admin

# Services externes
PRODUCT_SERVICE_URL=http://product-service:5001
SALES_SERVICE_URL=http://sales-service:5005
CUSTOMER_SERVICE_URL=http://customer-service:5002

# Timeouts et retry
SERVICE_TIMEOUT=30
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY=1

# Monitoring
PROMETHEUS_ENABLED=true
LOG_LEVEL=INFO
STRUCTURED_LOGS=true

# Feature flags
ENABLE_COMPENSATION=true
ENABLE_METRICS=true
ENABLE_HEALTH_CHECK=true
```

### docker-compose.yml - Service Saga
```yaml
saga-orchestrator:
  build: ./saga-orchestrator
  ports:
    - "5006:5006"
  environment:
    - DATABASE_URL=postgresql://log430:laboratoire@saga-db:5432/sagadb
    - PRODUCT_SERVICE_URL=http://product-service:5001
    - SALES_SERVICE_URL=http://sales-service:5005
    - CUSTOMER_SERVICE_URL=http://customer-service:5002
  depends_on:
    - saga-db
    - product-service
    - sales-service
  networks:
    - microservices-network
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:5006/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

## 🛠️ Développement et Debug

### Logs de Debug Détaillés

```bash
# Activer les logs debug
docker-compose exec saga-orchestrator \
  python -c "import logging; logging.getLogger().setLevel(logging.DEBUG)"

# Suivre les logs avec filtre
docker-compose logs -f saga-orchestrator | grep "SAGA_ID"

# Analyser les performances
docker-compose logs saga-orchestrator | \
  jq 'select(.processing_time_ms > 1000)' | \
  jq '.processing_time_ms' | \
  sort -n
```



### Monitoring en Temps Réel

```bash
# Dashboard en ligne de commande
watch -n 2 'curl -s http://localhost:5006/metrics | grep saga_total'

# Surveillance des erreurs
tail -f /var/log/saga-orchestrator.log | grep ERROR

# État des services
watch -n 5 'docker-compose ps'
```

---

## 🎯 Conclusion du Laboratoire

Ce laboratoire démontre une implémentation complète d'une **Saga orchestrée synchrone** avec :

✅ **Machine d'état robuste** : Gestion précise des transitions  
✅ **Compensation automatique** : Rollback en cas d'échec  
✅ **Observabilité complète** : Métriques, logs et dashboards  
✅ **Tests complets** : Scénarios de succès et d'échec  
✅ **Documentation détaillée** : ADR, diagrammes et guides  

L'architecture mise en place respecte les principes des systèmes distribués tout en maintenant la cohérence des données et la résilience aux pannes.

---