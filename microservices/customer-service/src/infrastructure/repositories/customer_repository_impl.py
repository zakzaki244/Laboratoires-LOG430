from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ...domain.entities.customer import Customer
from ...domain.repositories.customer_repository import CustomerRepository
from ...domain.value_objects.customer_value_objects import Email, Phone, Address, Password
from ..database.models import CustomerModel


class SqlCustomerRepository(CustomerRepository):
    """Implémentation SQLAlchemy du repository des clients"""
    
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, customer: Customer) -> Customer:
        """Sauvegarder un client"""
        try:
            if customer.id:
                customer_model = self._session.query(CustomerModel).filter(
                    CustomerModel.id == customer.id
                ).first()
                
                if not customer_model:
                    raise ValueError(f"Client non trouvé pour mise à jour: {customer.id}")
                
                customer_model.email = customer.email.value
                customer_model.first_name = customer.first_name
                customer_model.last_name = customer.last_name
                customer_model.phone = customer.phone.value
                customer_model.password_hash = customer.password.hashed_value
                customer_model.address = customer.address.to_dict()
                customer_model.is_active = customer.is_active
                customer_model.updated_at = customer.updated_at
                
            else:
                customer_model = CustomerModel(
                    email=customer.email.value,
                    first_name=customer.first_name,
                    last_name=customer.last_name,
                    phone=customer.phone.value,
                    password_hash=customer.password.hashed_value,
                    address=customer.address.to_dict(),
                    is_active=customer.is_active,
                    created_at=customer.created_at,
                    updated_at=customer.updated_at
                )
                self._session.add(customer_model)
            
            self._session.commit()
            self._session.refresh(customer_model)
            
            return self._model_to_entity(customer_model)
            
        except IntegrityError as e:
            self._session.rollback()
            raise ValueError(f"Erreur d'intégrité des données: {str(e)}")
        except Exception as e:
            self._session.rollback()
            raise Exception(f"Erreur lors de la sauvegarde: {str(e)}")
    
    def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """Récupérer un client par ID"""
        customer_model = self._session.query(CustomerModel).filter(
            CustomerModel.id == customer_id
        ).first()
        
        return self._model_to_entity(customer_model) if customer_model else None
    
    def get_by_email(self, email: Email) -> Optional[Customer]:
        """Récupérer un client par email"""
        customer_model = self._session.query(CustomerModel).filter(
            CustomerModel.email == email.value
        ).first()
        
        return self._model_to_entity(customer_model) if customer_model else None
    
    def get_all_active(self) -> List[Customer]:
        """Récupérer tous les clients actifs"""
        customer_models = self._session.query(CustomerModel).filter(
            CustomerModel.is_active == True
        ).all()
        
        return [self._model_to_entity(model) for model in customer_models]
    
    def delete(self, customer_id: str) -> None:
        """Supprimer un client"""
        customer_model = self._session.query(CustomerModel).filter(
            CustomerModel.id == customer_id
        ).first()
        
        if customer_model:
            self._session.delete(customer_model)
            self._session.commit()
    
    def email_exists(self, email: Email) -> bool:
        """Vérifier si un email existe déjà"""
        count = self._session.query(CustomerModel).filter(
            CustomerModel.email == email.value
        ).count()
        
        return count > 0
    
    def _model_to_entity(self, model: CustomerModel) -> Customer:
        """Convertir un modèle SQLAlchemy en entité Customer"""
        customer = Customer(
            id=str(model.id),
            email=Email(model.email),
            first_name=model.first_name,
            last_name=model.last_name,
            phone=Phone(model.phone),
            address=Address.from_dict(model.address),
            password=Password(model.password_hash),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
        
        return customer
