from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.db import Base
import datetime

class Store(Base):
    __tablename__ = "stores"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    products = relationship("Product", back_populates="store")