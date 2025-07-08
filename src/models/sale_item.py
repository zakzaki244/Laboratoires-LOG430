from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.db import Base


class SaleItem(Base):
    __tablename__ = "sale_items"
    __table_args__ = {'extend_existing': True}
    id         = Column(Integer, primary_key=True)
    sale_id    = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity   = Column(Integer)
    sale       = relationship("Sale", back_populates="items")
    product    = relationship("Product")