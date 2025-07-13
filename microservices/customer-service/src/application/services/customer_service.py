from typing import List, Optional
from ..dto.customer_dto import (
    CustomerRegistrationDTO, CustomerLoginDTO, CustomerUpdateDTO,
    PasswordChangeDTO, CustomerResponseDTO
)
from ...domain.entities.customer import Customer
from ...domain.repositories.customer_repository import CustomerRepository
from ...domain.value_objects.customer_value_objects import Email, Phone, Address, Password


class CustomerService:
    """Service applicatif pour la gestion des clients"""
    
    def __init__(self, customer_repository: CustomerRepository):
        self._customer_repository = customer_repository
    
    async def register_customer(self, registration_dto: CustomerRegistrationDTO) -> CustomerResponseDTO:
        """Inscrire un nouveau client"""
        try:
            email = Email(registration_dto.email)
            if await self._customer_repository.email_exists(email):
                raise ValueError(f"Un compte avec l'email {registration_dto.email} existe déjà")
            
            customer = Customer.create_new_customer(
                email=registration_dto.email,
                first_name=registration_dto.first_name,
                last_name=registration_dto.last_name,
                phone=registration_dto.phone,
                address_data=registration_dto.address,
                plain_password=registration_dto.password
            )
            
            saved_customer = await self._customer_repository.save(customer)
            
            return CustomerResponseDTO.from_entity(saved_customer)
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'inscription: {str(e)}")
    
    async def login_customer(self, login_dto: CustomerLoginDTO) -> CustomerResponseDTO:
        """Connecter un client"""
        try:
            email = Email(login_dto.email)
            customer = await self._customer_repository.get_by_email(email)
            
            if not customer:
                raise ValueError("Email ou mot de passe incorrect")
            
            if not customer.is_active:
                raise ValueError("Compte désactivé")
            
            if not customer.password.verify(login_dto.password):
                raise ValueError("Email ou mot de passe incorrect")
            
            return CustomerResponseDTO.from_entity(customer)
            
        except Exception as e:
            raise Exception(f"Erreur lors de la connexion: {str(e)}")
    
    async def get_customer(self, customer_id: str) -> Optional[CustomerResponseDTO]:
        """Récupérer un client par ID"""
        customer = await self._customer_repository.get_by_id(customer_id)
        return CustomerResponseDTO.from_entity(customer) if customer else None
    
    async def update_customer(self, customer_id: str, update_dto: CustomerUpdateDTO) -> CustomerResponseDTO:
        """Mettre à jour un client"""
        try:
            customer = await self._customer_repository.get_by_id(customer_id)
            if not customer:
                raise ValueError(f"Client non trouvé: {customer_id}")
            
            if update_dto.first_name:
                customer.first_name = update_dto.first_name.strip()
            
            if update_dto.last_name:
                customer.last_name = update_dto.last_name.strip()
            
            if update_dto.phone:
                customer.phone = Phone(update_dto.phone)
            
            if update_dto.address:
                customer.address = Address.from_dict(update_dto.address)
            
            updated_customer = await self._customer_repository.save(customer)
            
            return CustomerResponseDTO.from_entity(updated_customer)
            
        except Exception as e:
            raise Exception(f"Erreur lors de la mise à jour: {str(e)}")
    
    async def change_password(self, customer_id: str, password_dto: PasswordChangeDTO) -> CustomerResponseDTO:
        """Changer le mot de passe d'un client"""
        try:
            customer = await self._customer_repository.get_by_id(customer_id)
            if not customer:
                raise ValueError(f"Client non trouvé: {customer_id}")
            
            if not customer.password.verify(password_dto.current_password):
                raise ValueError("Mot de passe actuel incorrect")
            
            new_password = Password.create_from_plain(password_dto.new_password)
            customer.change_password(new_password)
            
            updated_customer = await self._customer_repository.save(customer)
            
            return CustomerResponseDTO.from_entity(updated_customer)
            
        except Exception as e:
            raise Exception(f"Erreur lors du changement de mot de passe: {str(e)}")
    
    async def deactivate_customer(self, customer_id: str) -> CustomerResponseDTO:
        """Désactiver un client"""
        try:
            customer = await self._customer_repository.get_by_id(customer_id)
            if not customer:
                raise ValueError(f"Client non trouvé: {customer_id}")
            
            customer.deactivate()
            updated_customer = await self._customer_repository.save(customer)
            
            return CustomerResponseDTO.from_entity(updated_customer)
            
        except Exception as e:
            raise Exception(f"Erreur lors de la désactivation: {str(e)}")
    
    async def get_all_active_customers(self) -> List[CustomerResponseDTO]:
        """Récupérer tous les clients actifs"""
        customers = await self._customer_repository.get_all_active()
        return [CustomerResponseDTO.from_entity(customer) for customer in customers]
