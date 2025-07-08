from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.db import Base
import datetime


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = {'extend_existing': True}
    id        = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    items     = relationship("SaleItem", back_populates="sale", cascade="all, delete")