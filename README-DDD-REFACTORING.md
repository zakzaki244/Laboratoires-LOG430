# Guide de Refactorisation DDD - Architecture Microservices

## 🏗️ Vue d'ensemble

Cette refactorisation transforme l'architecture monolithique en microservices utilisant les principes du **Domain-Driven Design (DDD)** et de l'**Architecture Hexagonale**. Chaque microservice suit une structure en couches bien définie pour séparer les responsabilités.

## 📋 Structure des Services Refactorisés

📁 src/
├── domain/           🧠 COUCHE MÉTIER
│   ├── value_objects/   • Objets de valeur immutables
│   ├── entities/        • Entités avec identité
│   └── repositories/    • Interfaces d'accès aux données
├── application/      🎯 COUCHE APPLICATION
│   ├── dto/            • Objets de transfert
│   └── services/       • Services d'application
├── infrastructure/   🔧 COUCHE INFRASTRUCTURE
│   ├── database/       • Modèles SQLAlchemy
│   └── repositories/   • Implémentations concrètes
└── presentation/     🌐 COUCHE PRÉSENTATION
    └── controllers/    • Contrôleurs HTTP
    
### Services Complètement Refactorisés
- ✅ **Customer Service** - Gestion des clients
- ✅ **Product Service** - Gestion des produits
- ✅ **Store Service** - Gestion des magasins
- ✅ **Sales Service** - Gestion des ventes

### Services avec Structure DDD Créée
- 📝 **Inventory Service** - Gestion des stocks
- 📝 **Cart Service** - Gestion des paniers
- 📝 **Checkout Service** - Gestion des commandes

## 🏛️ Architecture DDD par Couches

### 1. Domain Layer (`src/domain/`)
**Couche métier pure - Sans dépendances externes**

```
src/domain/
├── value_objects/     # Objets de valeur immutables
├── entities/          # Entités avec identité et cycle de vie
└── repositories/      # Interfaces des repositories
```

#### Value Objects
- **Immutables** et **sans identité**
- **Validation métier** intégrée
- Exemples : `Money`, `Email`, `Phone`, `Address`

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "CAD"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Le montant ne peut pas être négatif")
```

#### Entities
- **Identité unique** et **cycle de vie**
- **Logique métier** encapsulée
- Exemples : `Customer`, `Product`, `Sale`

```python
@dataclass
class Customer:
    id: Optional[int]
    email: Email
    password: Password
    profile: CustomerProfile
    
    def update_profile(self, new_profile: CustomerProfile) -> None:
        self.profile = new_profile
```

### 2. Application Layer (`src/application/`)
**Orchestration et logique d'application**

```
src/application/
├── dto/               # Data Transfer Objects
└── services/          # Services d'application
```

#### DTOs (Data Transfer Objects)
- **Objets de transfert** entre couches
- **Validation des entrées**
- Exemples : `CreateCustomerRequest`, `ProductResponse`

#### Services d'Application
- **Orchestration** des opérations métier
- **Transactions** et **coordination**
- **Validation** des règles métier

### 3. Infrastructure Layer (`src/infrastructure/`)
**Implémentations techniques**

```
src/infrastructure/
├── database/          # Modèles SQLAlchemy
└── repositories/      # Implémentations concrètes
```

#### Database Models
- **Modèles SQLAlchemy** pour la persistance
- **Mapping** entre entités et base de données

#### Repository Implementations
- **Implémentations concrètes** des interfaces
- **Accès aux données** via SQLAlchemy

### 4. Presentation Layer (`src/presentation/`)
**Interface utilisateur et API**

```
src/presentation/
└── controllers/       # Contrôleurs Flask
```

#### Controllers
- **Gestion des requêtes HTTP**
- **Sérialisation/Désérialisation**
- **Gestion des erreurs**

## 🎯 Principes DDD Implémentés

### 1. Ubiquitous Language
- **Vocabulaire commun** entre développeurs et experts métier
- **Noms explicites** dans le code
- **Cohérence** entre documentation et code

### 2. Bounded Contexts
- **Séparation claire** des domaines métier
- **Microservices** par contexte délimité
- **Interfaces** bien définies entre contextes

### 3. Aggregates
- **Racines d'agrégat** pour maintenir la cohérence
- **Transactions** limitées aux agrégats
- **Invariants métier** protégés

### 4. Domain Events
- **Événements métier** pour la communication
- **Découplage** entre services
- **Intégration** asynchrone

## 🔄 Patterns Architecturaux Utilisés

### 1. Hexagonal Architecture (Ports & Adapters)
- **Isolation** de la logique métier
- **Testabilité** améliorée
- **Flexibilité** des adaptateurs

### 2. Repository Pattern
- **Abstraction** de l'accès aux données
- **Testabilité** avec mocks
- **Indépendance** vis-à-vis de la persistance

### 3. Factory Pattern
- **Création** d'objets complexes
- **Encapsulation** de la logique de création
- **Flexibilité** d'instanciation

## 🚀 Avantages de cette Architecture

### 1. Maintenabilité
- **Séparation claire** des responsabilités
- **Code plus lisible** et organisé
- **Évolution** facilitée

### 2. Testabilité
- **Tests unitaires** isolés
- **Mocks** facilités par les interfaces
- **Couverture** de code améliorée

### 3. Évolutivité
- **Ajout** de nouvelles fonctionnalités simplifié
- **Modification** des règles métier localisée
- **Refactoring** sécurisé

### 4. Résilience
- **Gestion d'erreurs** centralisée
- **Validation** métier robuste
- **Isolation** des pannes

## 📝 Exemple d'Utilisation

### Création d'un Client

```python
# 1. Requête HTTP (Presentation Layer)
@app.route('/customers', methods=['POST'])
def create_customer():
    return customer_controller.create_customer()

# 2. Contrôleur (Presentation Layer)
def create_customer(self):
    data = request.json
    create_request = CreateCustomerRequest(
        email=data['email'],
        password=data['password']
    )
    customer = self.customer_service.create_customer(create_request)
    return jsonify(customer.__dict__)

# 3. Service d'Application (Application Layer)
def create_customer(self, request: CreateCustomerRequest) -> CustomerResponse:
    email = Email(request.email)
    password = Password(request.password)
    
    customer = Customer(
        id=None,
        email=email,
        password=password
    )
    
    saved_customer = self.customer_repository.save(customer)
    return self._to_response(saved_customer)

# 4. Repository (Infrastructure Layer)
def save(self, customer: Customer) -> Customer:
    model = CustomerModel(
        email=customer.email.value,
        password_hash=customer.password.hash
    )
    self.session.add(model)
    self.session.commit()
    return self._to_entity(model)
```

## 🔧 Configuration et Déploiement

### Lancement des Services
```bash
# Démarrer tous les microservices
./start-microservices.sh

# Tester les APIs
./test-ecommerce-apis.sh
```

### Variables d'Environnement
```bash
# Configuration des bases de données
DATABASE_URL=postgresql://user:password@host:port/database

# URLs des services
STORE_SERVICE_URL=http://store-service:5001
PRODUCT_SERVICE_URL=http://product-service:5002
```

## 📊 Métriques et Monitoring

### Prometheus
- **Métriques** automatiques par endpoint
- **Monitoring** des performances
- **Alerting** configuré

### Health Checks
- **Vérification** de l'état des services
- **Intégration** avec les orchestrateurs
- **Diagnostic** automatisé

## 🎓 Bonnes Pratiques

### 1. Nommage
- **Noms explicites** et métier
- **Conventions** cohérentes
- **Ubiquitous Language**

### 2. Validation
- **Validation** dans les Value Objects
- **Règles métier** dans les Entities
- **Contraintes** dans les Services

### 3. Gestion d'Erreurs
- **Exceptions métier** spécifiques
- **Codes d'erreur** HTTP appropriés
- **Messages** informatifs

### 4. Tests
- **Tests unitaires** par couche
- **Tests d'intégration** pour les repositories
- **Tests fonctionnels** pour les APIs

## 🔮 Évolutions Futures

### 1. Event Sourcing
- **Historique** des événements
- **Reconstruction** des états
- **Audit** complet

### 2. CQRS
- **Séparation** lecture/écriture
- **Optimisation** des requêtes
- **Scalabilité** améliorée

### 3. Saga Pattern
- **Transactions** distribuées
- **Compensation** automatique
- **Cohérence** éventuelle

## 📚 Ressources Supplémentaires

- [Domain-Driven Design](https://domainlanguage.com/ddd/)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Microservices Patterns](https://microservices.io/patterns/)

---

**Cette refactorisation DDD transforme votre architecture en un système robuste, maintenable et évolutif, prêt pour les défis du développement moderne.**
