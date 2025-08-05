# 🏗️ Saga Orchestrator - Laboratoire 6 LOG430

## 📋 Description

Ce service implémente une **Saga orchestrée synchrone** pour gérer le processus de commande dans l'architecture microservices e-commerce. La Saga coordonne les interactions entre les microservices pour assurer la cohérence des données et la gestion des échecs.

## 🎯 Objectifs

- **Saga orchestrée synchrone** : Coordination centralisée des microservices
- **Machine d'état** : Suivi de l'évolution des commandes
- **Gestion des échecs** : Mécanismes de compensation automatiques
- **Observabilité** : Métriques Prometheus et logs structurés

## 🔄 Flux de la Saga

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   INITIATED     │───▶│ STOCK_CHECKED   │───▶│ STOCK_RESERVED  │───▶│ PAYMENT_PROCESSED│
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     FAILED      │    │     FAILED      │    │     FAILED      │    │   CONFIRMED     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Étapes de la Saga :

1. **Vérification du stock** (`STOCK_CHECKED`)
   - Appel au service produit pour vérifier la disponibilité
   - Échec si stock insuffisant

2. **Réservation du stock** (`STOCK_RESERVED`)
   - Réserve les produits pour la commande
   - Réduit le stock disponible

3. **Traitement du paiement** (`PAYMENT_PROCESSED`)
   - Appel au service de vente pour le paiement
   - Échec si paiement refusé

4. **Confirmation de la commande** (`CONFIRMED`)
   - Crée la vente dans la base de données
   - État final de succès

## 🛠️ Installation et Déploiement

### Prérequis

- Docker et Docker Compose
- Python 3.11+
- Accès aux microservices existants (product, sales, customer)

### Déploiement avec Docker

```bash
# 1. Cloner le projet
git clone https://github.com/zakzaki244/Laboratoires-LOG430/tree/lab6 
cd Laboratoires-LOG430

# 2. Démarrer tous les services
docker-compose up -d

# 3. Vérifier que le saga orchestrator est démarré
docker-compose ps saga-orchestrator

# 4. Vérifier les logs
docker-compose logs saga-orchestrator
```

### Configuration

Le service utilise les variables d'environnement suivantes :

```env
DATABASE_URL=postgresql://log430:laboratoire@saga-db:5432/sagadb
SECRET_KEY=saga_secret_key
JWT_SECRET_KEY=jwt_secret_key
PRODUCT_SERVICE_URL=http://product-service:5000
SALES_SERVICE_URL=http://sales-service:5000
CUSTOMER_SERVICE_URL=http://customer-service:5000
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

### 3. Déclencher les compensations manuellement

```http
POST /api/saga/{order_id}/compensate
```

### 4. Métriques Prometheus

```http
GET /metrics
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

## 📊 Observabilité

### Métriques Prometheus

- `saga_total{status="success"}` : Nombre de Sagas réussies
- `saga_total{status="failed"}` : Nombre de Sagas échouées
- `saga_duration_seconds` : Durée d'exécution des Sagas
- `saga_step_duration_seconds{step="stock_check"}` : Durée de chaque étape

### Logs structurés

Les logs incluent :
- ID de la Saga
- Événements et transitions d'état
- Erreurs et compensations
- Durée d'exécution

## 🔧 Mécanismes de Compensation

### Compensation automatique

En cas d'échec, les compensations sont exécutées automatiquement :

1. **Annulation de réservation de stock** : Restaure le stock réservé
2. **Remboursement de paiement** : Annule le paiement effectué

### Ordre de compensation

Les compensations sont exécutées dans l'ordre inverse des opérations :

```
Paiement → Réservation → Vérification
   ↓           ↓            ↓
Remboursement → Libération → (Aucune)
```

## 🚨 Gestion des Erreurs

### Types d'erreurs gérées

- **Erreurs de communication** : Timeout, service indisponible
- **Erreurs métier** : Stock insuffisant, paiement refusé
- **Erreurs système** : Base de données, configuration

### Stratégies de récupération

- **Retry automatique** : Pour les erreurs temporaires
- **Compensation** : Pour les erreurs permanentes
- **Logging détaillé** : Pour le debugging

## 🔍 Monitoring et Debugging

### Vérifier l'état des services

```bash
# Vérifier que tous les services sont démarrés
docker-compose ps

# Vérifier les logs du saga orchestrator
docker-compose logs -f saga-orchestrator

# Vérifier les logs des microservices
docker-compose logs -f product-service
docker-compose logs -f sales-service
```

### Métriques Grafana

1. Accéder à Grafana : http://localhost:3000
2. Dashboard : "Saga Orchestrator Metrics"
3. Métriques disponibles :
   - Taux de succès des Sagas
   - Durée moyenne d'exécution
   - Nombre d'échecs par étape
   - Temps de compensation

## 📝 Cas d'usage

### Cas 1 : Commande réussie

1. Client passe une commande
2. Saga vérifie le stock → ✅
3. Saga réserve le stock → ✅
4. Saga traite le paiement → ✅
5. Saga confirme la commande → ✅
6. **Résultat** : Commande confirmée

### Cas 2 : Stock insuffisant

1. Client passe une commande
2. Saga vérifie le stock → ❌ (stock insuffisant)
3. **Résultat** : Saga échoue, aucune compensation nécessaire

### Cas 3 : Paiement refusé

1. Client passe une commande
2. Saga vérifie le stock → ✅
3. Saga réserve le stock → ✅
4. Saga traite le paiement → ❌ (refusé)
5. **Compensation** : Libération du stock réservé
6. **Résultat** : Saga annulée, stock restauré
