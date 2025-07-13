# 📚 Guide Complet de l'Architecture DDD des Microservices

## 🎯 Vue d'ensemble

Tous les microservices suivent maintenant l'architecture **Domain-Driven Design (DDD)** avec une séparation claire en 4 couches principales. Voici une explication détaillée de chaque composant :

---

## 🏗️ Structure Générale de chaque Microservice

```
microservice-name/
├── app.py                    # Point d'entrée Flask avec routes
├── requirements.txt          # Dépendances Python
├── Dockerfile               # Configuration Docker
└── src/                     # Code source DDD
    ├── domain/             # 🧠 COUCHE MÉTIER (DOMAIN)
    │   ├── value_objects/  # Objets de valeur immutables
    │   ├── entities/       # Entités avec identité
    │   └── repositories/   # Interfaces d'accès aux données
    ├── application/        # 🎯 COUCHE APPLICATION
    │   ├── dto/           # Objets de transfert de données
    │   └── services/      # Services d'application
    ├── infrastructure/    # 🔧 COUCHE INFRASTRUCTURE
    │   ├── database/      # Modèles de persistance SQLAlchemy
    │   └── repositories/  # Implémentations concrètes des repositories
    └── presentation/      # 🌐 COUCHE PRÉSENTATION
        └── controllers/   # Contrôleurs HTTP
```

---

## 📦 Description détaillée des Services

### 🛍️ **1. Customer Service (Port 5005)**
**Rôle** : Gestion des clients et de leurs informations

#### 🧠 Domain Layer
- **Value Objects** (`src/domain/value_objects/__init__.py`)
  - `Email` : Validation et gestion des emails
  - `PhoneNumber` : Format et validation des numéros de téléphone
  - `CustomerId` : Identifiant unique du client

- **Entities** (`src/domain/entities/__init__.py`)
  - `Customer` : Entité principale avec comportements métier
    - Méthodes : `activate()`, `deactivate()`, `update_contact_info()`
    - Validation : Email unique, téléphone valide

- **Repository Interfaces** (`src/domain/repositories/__init__.py`)
  - `CustomerRepository` : Interface abstraite pour l'accès aux données
    - Méthodes : `save()`, `find_by_id()`, `find_by_email()`, `find_all()`

#### 🎯 Application Layer
- **DTOs** (`src/application/dto/__init__.py`)
  - `CreateCustomerRequest` : Données pour créer un client
  - `UpdateCustomerRequest` : Données pour modifier un client
  - `CustomerResponse` : Réponse avec les données client

- **Services** (`src/application/services/__init__.py`)
  - `CustomerService` : Logique métier et orchestration
    - Validation des données d'entrée
    - Coordination entre les repositories
    - Transformation entities ↔ DTOs

#### 🔧 Infrastructure Layer
- **Database Models** (`src/infrastructure/database/__init__.py`)
  - `CustomerModel` : Modèle SQLAlchemy pour la persistance
  - Configuration de la base de données

- **Repository Implementations** (`src/infrastructure/repositories/__init__.py`)
  - `SQLAlchemyCustomerRepository` : Implémentation concrète
    - Mapping entre entités et modèles de données
    - Requêtes SQL via SQLAlchemy

#### 🌐 Presentation Layer
- **Controllers** (`src/presentation/controllers/__init__.py`)
  - `CustomerController` : Gestion des requêtes HTTP
    - Routes REST : GET, POST, PUT, DELETE
    - Sérialisation JSON
    - Gestion des erreurs HTTP

---

### 📦 **2. Product Service (Port 5002)**
**Rôle** : Gestion du catalogue de produits

#### 🧠 Domain Layer
- **Value Objects**
  - `ProductName` : Nom du produit avec validation
  - `Price` : Prix avec validation (>0, devise)
  - `SKU` : Référence produit unique

- **Entities**
  - `Product` : Entité produit avec comportements
    - Méthodes : `update_price()`, `activate()`, `deactivate()`
    - Validation : Prix positif, SKU unique

- **Repository Interfaces**
  - `ProductRepository` : Interface d'accès aux produits

#### 🎯 Application Layer
- **DTOs** : Requêtes et réponses pour les opérations produit
- **Services** : `ProductService` avec logique de gestion du catalogue

#### 🔧 Infrastructure Layer
- **Database Models** : `ProductModel` pour SQLAlchemy
- **Repository Implementations** : `SQLAlchemyProductRepository`

#### 🌐 Presentation Layer
- **Controllers** : `ProductController` avec routes REST

---

### 🏪 **3. Store Service (Port 5001)**
**Rôle** : Gestion des magasins et de leurs inventaires

#### 🧠 Domain Layer
- **Value Objects**
  - `StoreName` : Nom du magasin
  - `Address` : Adresse complète
  - `StoreId` : Identifiant unique

- **Entities**
  - `Store` : Entité magasin
    - Méthodes : `add_product()`, `update_stock()`, `remove_product()`
    - Validation : Stock positif, produits valides

- **Repository Interfaces**
  - `StoreRepository` : Interface d'accès aux magasins

#### 🎯 Application Layer
- **DTOs** : Gestion des requêtes de magasin et stock
- **Services** : `StoreService` avec logique d'inventaire

#### 🔧 Infrastructure Layer
- **Database Models** : `StoreModel`, `StockModel`
- **Repository Implementations** : `SQLAlchemyStoreRepository`

#### 🌐 Presentation Layer
- **Controllers** : `StoreController` avec gestion du stock

---

### 💰 **4. Sales Service (Port 5003)**
**Rôle** : Enregistrement et suivi des ventes

#### 🧠 Domain Layer
- **Value Objects**
  - `SaleAmount` : Montant de la vente
  - `SaleDate` : Date de la vente
  - `SaleId` : Identifiant unique

- **Entities**
  - `Sale` : Entité vente
    - Méthodes : `add_item()`, `calculate_total()`, `apply_discount()`
    - Validation : Montant positif, articles valides

- **Repository Interfaces**
  - `SaleRepository` : Interface d'accès aux ventes

#### 🎯 Application Layer
- **DTOs** : Création de vente, rapport de ventes
- **Services** : `SalesService` avec calculs et statistiques

#### 🔧 Infrastructure Layer
- **Database Models** : `SaleModel`, `SaleItemModel`
- **Repository Implementations** : `SQLAlchemySaleRepository`

#### 🌐 Presentation Layer
- **Controllers** : `SalesController` avec rapports et statistiques

---

### 🛒 **5. Cart Service (Port 5006)**
**Rôle** : Gestion des paniers d'achat

#### 🧠 Domain Layer
- **Value Objects**
  - `CartId` : Identifiant du panier
  - `Quantity` : Quantité d'articles
  - `ProductId` : Référence produit

- **Entities**
  - `Cart` : Entité panier
    - Méthodes : `add_item()`, `remove_item()`, `update_quantity()`, `clear()`
    - Validation : Quantité positive, produits existants

- **Repository Interfaces**
  - `CartRepository` : Interface d'accès aux paniers

#### 🎯 Application Layer
- **DTOs** : Opérations sur le panier
- **Services** : `CartService` avec validation des produits

#### 🔧 Infrastructure Layer
- **Database Models** : `CartModel`, `CartItemModel`
- **Repository Implementations** : `SQLAlchemyCartRepository`

#### 🌐 Presentation Layer
- **Controllers** : `CartController` avec opérations CRUD

---

### 📋 **6. Checkout Service (Port 5007)**
**Rôle** : Traitement des commandes et paiements

#### 🧠 Domain Layer
- **Value Objects** (`src/domain/value_objects/checkout_value_objects.py`)
  - `OrderNumber` : Numéro de commande unique
  - `Address` : Adresse de livraison/facturation
  - `Money` : Montant avec devise et calculs
  - `OrderStatus` : Statut de la commande (enum)
  - `PaymentStatus` : Statut du paiement (enum)

- **Entities** (`src/domain/entities/order.py`)
  - `Order` : Entité commande principale
    - Méthodes : `confirm()`, `cancel()`, `ship()`, `deliver()`
    - Calculs : `calculate_total()`, `calculate_subtotal()`
  - `OrderItem` : Article de commande

- **Repository Interfaces** (`src/domain/repositories/order_repository.py`)
  - `OrderRepository` : Interface d'accès aux commandes

#### 🎯 Application Layer
- **DTOs** (`src/application/dto/checkout_dto.py`)
  - `CreateOrderRequest`, `UpdateOrderRequest`, `ProcessPaymentRequest`
  - `OrderResponse`, `OrderListResponse`

- **Services** (`src/application/services/checkout_service.py`)
  - `CheckoutService` : Orchestration des commandes
    - Interaction avec cart-service, product-service
    - Calcul des taxes et frais de livraison
    - Traitement des paiements

#### 🔧 Infrastructure Layer
- **Database Models** (`src/infrastructure/database/models.py`)
  - `OrderModel`, `OrderItemModel` : Persistance SQLAlchemy

- **Repository Implementations** (`src/infrastructure/repositories/sqlalchemy_order_repository.py`)
  - `SQLAlchemyOrderRepository` : Implémentation concrète

#### 🌐 Presentation Layer
- **Controllers** (`src/presentation/controllers/checkout_controller.py`)
  - `CheckoutController` : API REST pour les commandes

---

### 📦 **7. Inventory Service (Port 5008)**
**Rôle** : Gestion des demandes de réapprovisionnement

#### 🧠 Domain Layer
- **Value Objects** (`src/domain/value_objects/inventory_value_objects.py`)
  - `StoreId`, `ProductId`, `Quantity` : Identifiants et quantités
  - `ReapproStatus` : Statut de la demande (enum)

- **Entities** (`src/domain/entities/reappro_request.py`)
  - `ReapproRequest` : Demande de réapprovisionnement
    - Méthodes : `approve()`, `reject()`, `complete()`
    - Validation : Quantité positive, statuts valides

- **Repository Interfaces** (`src/domain/repositories/reappro_request_repository.py`)
  - `ReapproRequestRepository` : Interface d'accès aux demandes

#### 🎯 Application Layer
- **DTOs** (`src/application/dto/inventory_dto.py`)
  - `CreateReapproRequest`, `UpdateReapproRequest`
  - `ReapproRequestResponse`, `ReapproStatsResponse`

- **Services** (`src/application/services/inventory_service.py`)
  - `InventoryService` : Gestion des réapprovisionnements
    - Validation avec product-service et store-service
    - Statistiques et rapports

#### 🔧 Infrastructure Layer
- **Database Models** (`src/infrastructure/database/models.py`)
  - `ReapproRequestModel` : Persistance SQLAlchemy

- **Repository Implementations** (`src/infrastructure/repositories/sqlalchemy_reappro_request_repository.py`)
  - `SQLAlchemyReapproRequestRepository` : Implémentation concrète

#### 🌐 Presentation Layer
- **Controllers** (`src/presentation/controllers/inventory_controller.py`)
  - `InventoryController` : API REST pour les demandes

---

## 🔗 **8. API Gateway (Port 8080)**
**Rôle** : Point d'entrée unique, routage et load balancing

- Routage des requêtes vers les services appropriés
- Load balancing entre les instances
- Authentification centralisée
- Limitation de taux (rate limiting)

---

## 🎯 Principes DDD Appliqués

### 1. **Ubiquitous Language**
- Vocabulaire métier partagé entre développeurs et experts métier
- Classes et méthodes nommées selon le domaine

### 2. **Bounded Contexts**
- Chaque service a sa responsabilité claire
- Séparation des domaines métier

### 3. **Value Objects**
- Objets immutables avec validation intégrée
- Pas d'identité, définis par leurs valeurs

### 4. **Entities**
- Objets avec identité unique
- Comportements métier encapsulés

### 5. **Aggregates**
- Cohérence des données dans les entités
- Transactions limitées aux agrégats

### 6. **Repository Pattern**
- Abstraction de l'accès aux données
- Interface dans le domain, implémentation dans l'infrastructure

### 7. **Layered Architecture**
- Séparation claire des responsabilités
- Dépendances dirigées vers le domain

---

## 🚀 Avantages de cette Architecture

### ✅ **Maintenabilité**
- Code bien organisé et structuré
- Responsabilités clairement définies
- Facilité de modification

### ✅ **Testabilité**
- Injection de dépendances
- Interfaces mockables
- Tests unitaires par couche

### ✅ **Évolutivité**
- Ajout de fonctionnalités simplifié
- Architecture extensible
- Services indépendants

### ✅ **Robustesse**
- Validation dans les Value Objects
- Règles métier dans les entités
- Gestion d'erreurs centralisée

### ✅ **Réutilisabilité**
- Services découplés
- Interfaces bien définies
- Code partageable

---

## 🔄 Flux de Données Typique

1. **Request HTTP** → `Controller` (Presentation)
2. **Validation** → `DTO` (Application)
3. **Logique métier** → `Service` (Application)
4. **Règles métier** → `Entity/Value Object` (Domain)
5. **Persistance** → `Repository` (Infrastructure)
6. **Response** → `DTO` → `Controller` → **HTTP Response**

---

Cette architecture garantit un code maintenable, testable et évolutif, respectant les meilleures pratiques DDD ! 🎉
