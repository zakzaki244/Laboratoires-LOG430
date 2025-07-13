from .customer_repository_impl import SqlCustomerRepository

# Alias pour simplifier les imports
CustomerRepository = SqlCustomerRepository

__all__ = ['CustomerRepository', 'SqlCustomerRepository']
