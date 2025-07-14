"""
Seed data for customer service
"""

from .models import CustomerModel
from werkzeug.security import generate_password_hash

def seed_default_users(session):
    """Seed default users if they don't exist"""
    try:
        # Check if admin user exists
        admin_user = session.query(CustomerModel).filter_by(email='admin@example.com').first()
        if not admin_user:
            admin_user = CustomerModel(
                first_name='Admin',
                last_name='User',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                store_id=1,
                phone='514-000-0001',
                address={
                    'street': '123 Admin St',
                    'city': 'Montreal',
                    'postal_code': 'H1A 1A1',
                    'country': 'Canada'
                }
            )
            session.add(admin_user)
            print("Admin user created")
        
        # Check if manager user exists
        manager_user = session.query(CustomerModel).filter_by(email='manager@example.com').first()
        if not manager_user:
            manager_user = CustomerModel(
                first_name='Manager',
                last_name='User',
                email='manager@example.com',
                password_hash=generate_password_hash('manager123'),
                role='manager',
                store_id=1,
                phone='514-000-0002',
                address={
                    'street': '456 Manager Ave',
                    'city': 'Montreal',
                    'postal_code': 'H2B 2B2',
                    'country': 'Canada'
                }
            )
            session.add(manager_user)
            print("Manager user created")
        
        # Check if employee user exists
        employee_user = session.query(CustomerModel).filter_by(email='employee@example.com').first()
        if not employee_user:
            employee_user = CustomerModel(
                first_name='Employee',
                last_name='User',
                email='employee@example.com',
                password_hash=generate_password_hash('employee123'),
                role='employee',
                store_id=1,
                phone='514-000-0003',
                address={
                    'street': '789 Employee Blvd',
                    'city': 'Montreal',
                    'postal_code': 'H3C 3C3',
                    'country': 'Canada'
                }
            )
            session.add(employee_user)
            print("Employee user created")
        
        session.commit()
        print("Default users seeded successfully")
        
    except Exception as e:
        print(f"Error seeding users: {e}")
        session.rollback()

def seed_stores():
    """Seed default stores if they don't exist"""
    try:
        # Note: In a real microservices architecture, stores would be managed by store-service
        # This is a simplified version for the customer service
        print("Store seeding would be handled by store-service in production")
        
    except Exception as e:
        print(f"Error seeding stores: {e}")
