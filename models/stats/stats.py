from sqlalchemy import Column, Integer, String, BigInteger, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class ProductVisitHistory(Base):
    __tablename__ = "product_visit_history"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    visit_date = Column(Date, nullable=False)
    total_visits = Column(Integer, nullable=False)
    unique_visits = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_product_date', 'product_id', 'visit_date'),
        {'extend_existing': True}
    )

class ProductVisitDetails(Base):
    __tablename__ = "product_visit_details"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    client_ip = Column(String(45), nullable=False)
    visit_timestamp = Column(DateTime, nullable=False)
    user_agent = Column(String(255))
    referrer = Column(String(255))
    session_id = Column(String(100))
    user_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_product_id', 'product_id'),
        Index('idx_visit_timestamp', 'visit_timestamp'),
        {'extend_existing': True}
    )