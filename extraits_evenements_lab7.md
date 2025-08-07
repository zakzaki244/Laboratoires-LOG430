# Extraits d'Événements Lab 7 - Succès et Compensation

## 🎯 Événements de Succès - Saga de Réapprovisionnement

### 1. Événement Déclencheur : Vente de Produit

```json
{
  "event_id": "evt_b4c7d2a1-8e4f-4c8a-9d6b-123456789abc",
  "event_type": "ProductSold",
  "aggregate_id": "product_LAPTOP_GAMING_001",
  "aggregate_type": "Product",
  "timestamp": "2025-08-07T14:30:15.123Z",
  "version": 1,
  "correlation_id": "saga_restock_20250807_143015",
  "data": {
    "product_id": "LAPTOP_GAMING_001",
    "quantity": 15,
    "customer_id": "customer_john_doe_789",
    "order_id": "order_987654321",
    "price": 1299.99,
    "total_amount": 19499.85,
    "store_id": "store_montreal_001"
  }
}
```

### 2. Mise à Jour du Stock

```json
{
  "event_id": "evt_c8d9e2f3-1a5b-4d7e-8f9c-234567890def",
  "event_type": "StockUpdated", 
  "aggregate_id": "inventory_LAPTOP_GAMING_001",
  "aggregate_type": "Inventory",
  "timestamp": "2025-08-07T14:30:16.456Z",
  "version": 2,
  "correlation_id": "saga_restock_20250807_143015",
  "data": {
    "product_id": "LAPTOP_GAMING_001",
    "previous_quantity": 50,
    "new_quantity": 35,
    "operation": "subtract",
    "reason": "product_sold",
    "order_id": "order_987654321"
  }
}
```

### 3. Détection de Stock Bas (Déclencheur Saga)

```json
{
  "event_id": "evt_d9e0f3g4-2b6c-5e8f-9g0d-345678901fed",
  "event_type": "LowStockDetected",
  "aggregate_id": "inventory_LAPTOP_GAMING_001", 
  "aggregate_type": "Inventory",
  "timestamp": "2025-08-07T14:30:17.789Z",
  "version": 3,
  "correlation_id": "saga_restock_20250807_143015",
  "data": {
    "product_id": "LAPTOP_GAMING_001",
    "current_quantity": 35,
    "threshold": 40,
    "requested_quantity": 50,
    "priority": "medium",
    "estimated_cost": 15000.00,
    "preferred_supplier": "supplier_tech_solutions_001"
  }
}
```

### 4. Approbation de Réapprovisionnement

```json
{
  "event_id": "evt_e0f1g4h5-3c7d-6f9g-0h1e-456789012gfe",
  "event_type": "RestockApproved",
  "aggregate_id": "procurement_order_789456123",
  "aggregate_type": "ProcurementOrder", 
  "timestamp": "2025-08-07T14:30:25.321Z",
  "version": 1,
  "correlation_id": "saga_restock_20250807_143015",
  "data": {
    "product_id": "LAPTOP_GAMING_001",
    "quantity": 50,
    "supplier_id": "supplier_tech_solutions_001",
    "order_id": "procurement_order_789456123",
    "estimated_cost": 15000.00,
    "budget_approved": true,
    "expected_delivery": "2025-08-07T16:30:00.000Z",
    "approval_reason": "automatic_approval_within_budget"
  }
}
```

### 5. Début de Livraison Fournisseur

```json
{
  "event_id": "evt_f1g2h5i6-4d8e-7g0h-1i2f-567890123hgf",
  "event_type": "DeliveryStarted",
  "aggregate_id": "delivery_DEL_789456123_001",
  "aggregate_type": "Delivery",
  "timestamp": "2025-08-07T14:32:10.654Z", 
  "version": 1,
  "correlation_id": "saga_restock_20250807_143015",
  "data": {
    "order_id": "procurement_order_789456123",
    "supplier_id": "supplier_tech_solutions_001",
    "delivery_id": "delivery_DEL_789456123_001",
    "estimated_delivery": "2025-08-07T16:30:00.000Z",
    "tracking_number": "TRK_20250807_789456",
    "driver_id": "driver_montreal_012",
    "vehicle_id": "truck_MTL_789"
  }
}
```

### 6. Livraison Réussie

```json
{
  "event_id": "evt_g2h3i6j7-5e9f-8h1i-2j3g-678901234ihg",
  "event_type": "SupplierDelivered",
  "aggregate_id": "delivery_DEL_789456123_001",
  "aggregate_type": "Delivery",
  "timestamp": "2025-08-07T16:25:30.987Z",
  "version": 2, 
  "correlation_id": "saga_restock_20250807_143015",
  "data": {
    "product_id": "LAPTOP_GAMING_001",
    "quantity": 50,
    "order_id": "procurement_order_789456123",
    "supplier_id": "supplier_tech_solutions_001",
    "delivery_id": "delivery_DEL_789456123_001",
    "actual_delivery_time": "2025-08-07T16:25:30.987Z",
    "delivery_duration_minutes": 115,
    "quality_check_passed": true,
    "received_by": "warehouse_employee_marie_001"
  }
}
```

### 7. Finalisation - Stock Mis à Jour

```json
{
  "event_id": "evt_h3i4j7k8-6f0g-9i2j-3k4h-789012345jih",
  "event_type": "StockUpdated",
  "aggregate_id": "inventory_LAPTOP_GAMING_001",
  "aggregate_type": "Inventory", 
  "timestamp": "2025-08-07T16:26:45.123Z",
  "version": 4,
  "correlation_id": "saga_restock_20250807_143015",
  "data": {
    "product_id": "LAPTOP_GAMING_001",
    "previous_quantity": 35,
    "new_quantity": 85,
    "operation": "add",
    "reason": "supplier_delivery_received",
    "delivery_id": "delivery_DEL_789456123_001",
    "restock_completed": true
  }
}
```

---

## ❌ Événements de Compensation - Saga d'Échec

### Scénario : Fournisseur ne peut pas livrer

### 1. Échec de Livraison Fournisseur

```json
{
  "event_id": "evt_i4j5k8l9-7g1h-0j3k-4l5i-890123456kji",
  "event_type": "SupplierDeliveryFailed",
  "aggregate_id": "delivery_DEL_789456124_FAIL",
  "aggregate_type": "Delivery",
  "timestamp": "2025-08-07T16:45:12.456Z",
  "version": 1,
  "correlation_id": "saga_restock_fail_20250807_164512",
  "data": {
    "order_id": "procurement_order_789456124",
    "supplier_id": "supplier_tech_solutions_001", 
    "delivery_id": "delivery_DEL_789456124_FAIL",
    "failure_reason": "insufficient_supplier_stock",
    "failure_code": "SUPPLIER_OUT_OF_STOCK",
    "expected_delivery": "2025-08-07T16:30:00.000Z",
    "failure_time": "2025-08-07T16:45:12.456Z",
    "retry_possible": false,
    "alternative_suppliers": ["supplier_tech_backup_002", "supplier_electronics_global_003"]
  }
}
```

### 2. Compensation - Annulation de Commande

```json
{
  "event_id": "evt_j5k6l9m0-8h2i-1k4l-5m6j-901234567lkj", 
  "event_type": "RestockCancelled",
  "aggregate_id": "procurement_order_789456124",
  "aggregate_type": "ProcurementOrder",
  "timestamp": "2025-08-07T16:46:05.789Z",
  "version": 2,
  "correlation_id": "saga_restock_fail_20250807_164512",
  "data": {
    "original_order_id": "procurement_order_789456124",
    "product_id": "LAPTOP_GAMING_001",
    "cancelled_quantity": 50,
    "reason": "supplier_delivery_failed",
    "compensation_action": "order_cancellation",
    "compensates_event": "evt_e0f1g4h5-3c7d-6f9g-0h1e-456789012gfe",
    "budget_released": 15000.00,
    "cancellation_time": "2025-08-07T16:46:05.789Z"
  }
}
```

### 3. Compensation - Recherche Fournisseur Alternatif

```json
{
  "event_id": "evt_k6l7m0n1-9i3j-2l5m-6n7k-012345678mlk",
  "event_type": "AlternativeSupplierRequested", 
  "aggregate_id": "procurement_request_ALT_789456124",
  "aggregate_type": "ProcurementRequest",
  "timestamp": "2025-08-07T16:46:30.012Z",
  "version": 1,
  "correlation_id": "saga_restock_fail_20250807_164512",
  "data": {
    "product_id": "LAPTOP_GAMING_001",
    "original_order_id": "procurement_order_789456124",
    "failed_supplier": "supplier_tech_solutions_001",
    "alternative_suppliers": [
      {
        "supplier_id": "supplier_tech_backup_002",
        "estimated_cost": 16500.00,
        "estimated_delivery": "2025-08-08T10:00:00.000Z",
        "reliability_score": 0.92
      },
      {
        "supplier_id": "supplier_electronics_global_003", 
        "estimated_cost": 15800.00,
        "estimated_delivery": "2025-08-08T14:00:00.000Z",
        "reliability_score": 0.88
      }
    ],
    "urgency_level": "high",
    "auto_approval_threshold": 20000.00
  }
}
```

### 4. Compensation - Alerte Stock Critique

```json
{
  "event_id": "evt_l7m8n1o2-0j4k-3m6n-7o8l-123456789nml",
  "event_type": "LowStockAlert",
  "aggregate_id": "inventory_LAPTOP_GAMING_001",
  "aggregate_type": "Inventory", 
  "timestamp": "2025-08-07T16:47:15.345Z",
  "version": 5,
  "correlation_id": "saga_restock_fail_20250807_164512",
  "data": {
    "product_id": "LAPTOP_GAMING_001",
    "current_quantity": 35,
    "critical_threshold": 30,
    "alert_level": "HIGH",
    "manual_intervention_required": true,
    "failed_restock_attempts": 1,
    "time_until_stockout_hours": 24,
    "business_impact": "potential_sales_loss",
    "escalation_required": true,
    "notify_managers": ["manager_inventory_montreal", "manager_procurement_central"]
  }
}
```

---

## 🔄 Exemple de Relecture d'Événements (Event Replay)

### Reconstruction de l'État du Stock pour LAPTOP_GAMING_001

```bash
# Commande de replay
curl -X POST http://localhost:5000/events/replay \
  -H "Content-Type: application/json" \
  -d '{
    "aggregate_id": "inventory_LAPTOP_GAMING_001",
    "from_timestamp": "2025-08-07T00:00:00.000Z",
    "to_timestamp": "2025-08-07T23:59:59.999Z"
  }'
```

### Résultat de la Relecture

```json
{
  "replay_id": "replay_20250807_170000_001",
  "aggregate_id": "inventory_LAPTOP_GAMING_001", 
  "events_replayed": 7,
  "state_reconstruction": {
    "initial_state": {
      "quantity": 100,
      "last_restock": "2025-08-05T10:00:00.000Z"
    },
    "events_applied": [
      {
        "timestamp": "2025-08-07T09:15:30.000Z",
        "event_type": "ProductSold",
        "quantity_change": -10,
        "running_total": 90
      },
      {
        "timestamp": "2025-08-07T11:22:45.000Z", 
        "event_type": "ProductSold",
        "quantity_change": -5,
        "running_total": 85
      },
      {
        "timestamp": "2025-08-07T14:30:16.456Z",
        "event_type": "ProductSold", 
        "quantity_change": -15,
        "running_total": 70
      },
      {
        "timestamp": "2025-08-07T14:30:16.456Z",
        "event_type": "StockUpdated",
        "quantity_change": -35,
        "running_total": 35,
        "note": "Correction après vente de 15 unités"
      },
      {
        "timestamp": "2025-08-07T16:26:45.123Z",
        "event_type": "StockUpdated",
        "quantity_change": +50, 
        "running_total": 85,
        "note": "Réapprovisionnement fournisseur"
      }
    ],
    "final_state": {
      "quantity": 85,
      "status": "adequate_stock",
      "last_update": "2025-08-07T16:26:45.123Z",
      "total_sales_today": 30,
      "restocks_today": 1
    }
  },
  "replay_duration_ms": 234,
  "timestamp": "2025-08-07T17:00:00.123Z"
}
```

---

## 📊 Métriques des Événements

### Statistiques de Performance

```json
{
  "event_statistics": {
    "total_events_today": 1247,
    "events_by_type": {
      "ProductSold": 421,
      "StockUpdated": 398, 
      "LowStockDetected": 23,
      "RestockApproved": 18,
      "SupplierDelivered": 15,
      "RestockCancelled": 3,
      "LowStockAlert": 8
    },
    "saga_statistics": {
      "successful_sagas": 15,
      "failed_sagas": 3,
      "compensation_events": 8,
      "average_saga_duration_minutes": 118,
      "success_rate": 0.833
    },
    "performance_metrics": {
      "average_event_processing_ms": 45,
      "events_per_second_peak": 127,
      "event_store_size_mb": 234.7,
      "projection_update_latency_ms": 23
    }
  }
}
```