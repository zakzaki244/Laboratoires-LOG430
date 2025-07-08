from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.db import Base

class ReapproRequest(Base):
    __tablename__ = "reappro_requests"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    status = Column(String, default="en attente")  # "en attente", "validée"
    requested_by = Column(String)  # username ou user_id
    # relations ORM pour facilité
    store = relationship("Store")
    product = relationship("Product")