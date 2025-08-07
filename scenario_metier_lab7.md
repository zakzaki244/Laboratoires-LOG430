# Scénario Métier Lab 7 - Gestion Automatique du Stock E-commerce

## 🎯 Contexte Métier

**Domaine** : Plateforme e-commerce avec gestion automatisée des stocks  
**Problématique** : Comment maintenir automatiquement des niveaux de stock optimaux sans intervention manuelle constante ?

## 📋 Scénario Principal : "Réapprovisionnement Automatique Intelligent"

### Acteurs
- **Client** : Effectue des achats sur la plateforme
- **Gestionnaire de Stock** : Supervise les niveaux globaux (consultation)
- **Fournisseurs** : Approvisionnent automatiquement selon les besoins
- **Système** : Gère automatiquement tout le processus

### Objectif Métier
Assurer une disponibilité constante des produits en automatisant le processus de réapprovisionnement depuis la détection de stock bas jusqu'à la livraison, tout en maintenant une traçabilité complète.

---

## 🔄 Flux Métier Détaillé

### Phase 1 : Déclenchement (Vente Client)
```
Préconditions :
- Client authentifié
- Produit disponible en stock
- Stock actuel : 50 unités, seuil critique : 40 unités

Action : Client achète 15 unités du produit "LAPTOP_GAMING_001"
```

**Événements générés :**
- `ProductSold` : Enregistre la vente
- `StockUpdated` : Stock passe à 35 unités
- `LowStockDetected` : Seuil critique atteint (35 < 40)

### Phase 2 : Analyse et Décision (Procurement automatique)
```
Le service Procurement reçoit l'alerte et évalue :
- Budget disponible : 50 000€
- Coût estimé réapprovisionnement : 15 000€ 
- Fournisseur préférentiel disponible : Oui
- Délai acceptable : 2 heures
```

**Événements générés :**
- `RestockRequested` : Demande de réapprovisionnement
- `RestockApproved` : Commande approuvée (50 unités)

### Phase 3 : Exécution Fournisseur (Livraison)
```
Le fournisseur SUP_TECH_001 :
- Vérifie son stock : 200 unités disponibles
- Confirme la livraison sous 2h
- Prépare la commande ORD_789123
```

**Événements générés :**
- `DeliveryStarted` : Livraison en cours
- `SupplierDelivered` : 50 unités livrées avec succès

### Phase 4 : Finalisation (Mise à jour stock)
```
Réception de la livraison :
- Stock mis à jour : 35 + 50 = 85 unités
- Seuil critique dépassé : ✅
- Disponibilité client rétablie : ✅
```

**Événements générés :**
- `StockUpdated` : Nouveau stock 85 unités
- `RestockCompleted` : Saga terminée avec succès

---

## ❌ Scénarios d'Échec et Compensation

### Scénario d'Échec 1 : Fournisseur Indisponible
```
Situation : Le fournisseur principal n'a plus de stock

Flux de compensation :
1. SupplierDeliveryFailed → Le fournisseur signale l'échec
2. RestockCancelled → Annulation de la commande initiale  
3. AlternativeSupplierRequested → Recherche fournisseur alternatif
4. LowStockAlert → Alerte pour intervention manuelle si aucune alternative
```

### Scénario d'Échec 2 : Budget Insuffisant
```
Situation : Le coût dépasse le budget autorisé

Flux de compensation :
1. RestockRejected → Rejet pour raison budgétaire
2. LowStockAlert → Escalade vers gestionnaire
3. ManualApprovalRequired → Demande d'approbation manuelle
```

### Scénario d'Échec 3 : Délai de Livraison Dépassé
```
Situation : La livraison n'arrive pas dans les temps

Flux de compensation :
1. DeliveryDelayed → Notification de retard
2. CustomerNotification → Information clients potentiels
3. AlternativeSupplierActivated → Commande de secours si critique
```

---

## 📊 Événements Métier Identifiés

### Événements de Démarrage
- `ProductSold` - Vente initiale déclenchant le processus
- `StockLevelChanged` - Modification du niveau de stock
- `LowStockDetected` - Seuil critique atteint

### Événements de Processus
- `RestockRequested` - Demande de réapprovisionnement
- `RestockApproved` / `RestockRejected` - Décision sur la demande
- `DeliveryStarted` - Début de livraison fournisseur
- `SupplierDelivered` - Livraison réussie

### Événements de Compensation
- `RestockCancelled` - Annulation de commande
- `SupplierDeliveryFailed` - Échec de livraison
- `LowStockAlert` - Alerte pour intervention manuelle
- `StockAdjusted` - Correction manuelle de stock

### Événements de Finalisation
- `StockUpdated` - Mise à jour finale du stock
- `RestockCompleted` - Fin de saga avec succès
- `SagaFailed` - Fin de saga avec échec

---

## 🎯 Valeur Métier

### Avantages Immédiats
- **Réactivité** : Réapprovisionnement automatique en < 3 heures
- **Disponibilité** : Réduction des ruptures de stock de 80%
- **Efficacité** : Réduction du travail manuel de 90%
- **Traçabilité** : Historique complet de toutes les décisions

### Métriques de Succès
- Taux de disponibilité produits : > 95%
- Temps moyen de réapprovisionnement : < 2 heures
- Taux de succès des sagas : > 98%
- Coût de gestion réduit de 60%

### ROI Estimé
- Économies annuelles : 200 000€ (réduction personnel + ventes perdues évitées)
- Investissement développement : 50 000€
- ROI : 300% sur 12 mois

---

## 🔧 Implémentation Technique

Ce scénario métier est implémenté via :
- **Event Sourcing** : Tous les événements métier persistés
- **CQRS** : Projections optimisées pour dashboards métier
- **Pub/Sub** : Communication asynchrone entre services métier
- **Saga Chorégraphiée** : Coordination automatique sans orchestrateur central

L'architecture garantit la traçabilité complète, la résilience aux pannes, et la scalabilité pour des millions de transactions.
