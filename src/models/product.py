from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.db import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = {'extend_existing': True}
    id       = Column(Integer, primary_key=True)
    name     = Column(String, index=True)
    category = Column(String, index=True)
    price    = Column(Float)
    stock    = Column(Integer, default=0)
    store_id = Column(Integer, ForeignKey('stores.id'))   
    store = relationship("Store", back_populates="products")
