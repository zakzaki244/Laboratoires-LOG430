import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database import Base
from src.application.services import ProductService
from src.application.dto.product_dto import (
    CreateProductRequest,
    UpdateProductRequest,
)
from src.infrastructure.repositories.product_repository_impl import ProductRepository


class DummyStoreServiceAdapter:
    def store_exists(self, store_id: int) -> bool:
        return True


@pytest.fixture
def session_factory():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)


@pytest.fixture
def product_service(session_factory):
    repo = ProductRepository(session_factory)
    adapter = DummyStoreServiceAdapter()
    return ProductService(repo, adapter)


def test_crud_flow(product_service):
    # Create product
    create_req = CreateProductRequest(name='Test', category='Cat', price=1.0, store_id=1)
    product = product_service.create_product(create_req)
    pid = product.id
    assert pid is not None

    # Get product
    fetched = product_service.get_product_by_id(pid)
    assert fetched is not None

    # Update product
    update_req = UpdateProductRequest(price=2.0)
    updated = product_service.update_product(pid, update_req)
    assert updated.price == 2.0

    # List products
    all_products = product_service.get_all_products()
    assert len(all_products) == 1

    # Search
    results = product_service.search_products('Test')
    assert len(results) == 1

    # Delete product
    assert product_service.delete_product(pid)
    assert product_service.get_product_by_id(pid) is None

