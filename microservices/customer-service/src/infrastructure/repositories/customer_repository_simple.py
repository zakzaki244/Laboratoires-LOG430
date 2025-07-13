from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database.models import CustomerModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SqlCustomerRepository:
    """Repository simple pour les clients utilisant SQLAlchemy"""
    
    def __init__(self, session_factory):
        self._session_factory = session_factory
    
    def _get_session(self):
        """Obtenir une session SQLAlchemy"""
        return self._session_factory()
    
    def create(self, customer_data: dict) -> CustomerModel:
        """Créer un nouveau client"""
        session = self._get_session()
        try:
            # Création du modèle
            customer = CustomerModel(
                email=customer_data['email'],
                first_name=customer_data['first_name'],
                last_name=customer_data['last_name'],
                phone=customer_data['phone'],
                password_hash=customer_data['password_hash'],
                address=customer_data['address'],
                is_active=customer_data.get('is_active', True),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(customer)
            session.commit()
            session.refresh(customer)
            return customer
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Erreur d'intégrité lors de la création du client: {str(e)}")
            raise ValueError("Email déjà utilisé")
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur lors de la création du client: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_by_email(self, email: str) -> Optional[CustomerModel]:
        """Récupérer un client par email"""
        session = self._get_session()
        try:
            return session.query(CustomerModel).filter_by(email=email).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du client par email: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_by_id(self, customer_id: int) -> Optional[CustomerModel]:
        """Récupérer un client par ID"""
        session = self._get_session()
        try:
            return session.query(CustomerModel).filter_by(id=customer_id).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du client par ID: {str(e)}")
            return None
        finally:
            session.close()
    
    def update(self, customer_id: int, update_data: dict) -> Optional[CustomerModel]:
        """Mettre à jour un client"""
        session = self._get_session()
        try:
            customer = session.query(CustomerModel).filter_by(id=customer_id).first()
            if not customer:
                return None
            
            # Mettre à jour les champs
            for key, value in update_data.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)
            
            customer.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(customer)
            return customer
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur lors de la mise à jour du client: {str(e)}")
            return None
        finally:
            session.close()
    
    def delete(self, customer_id: int) -> bool:
        """Supprimer un client"""
        session = self._get_session()
        try:
            customer = session.query(CustomerModel).filter_by(id=customer_id).first()
            if not customer:
                return False
            
            session.delete(customer)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur lors de la suppression du client: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_all(self) -> List[CustomerModel]:
        """Récupérer tous les clients"""
        session = self._get_session()
        try:
            return session.query(CustomerModel).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des clients: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_active_customers(self) -> List[CustomerModel]:
        """Récupérer tous les clients actifs"""
        session = self._get_session()
        try:
            return session.query(CustomerModel).filter_by(is_active=True).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des clients actifs: {str(e)}")
            return []
        finally:
            session.close()
