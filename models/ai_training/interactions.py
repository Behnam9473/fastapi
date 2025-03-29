# from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Text
# from sqlalchemy.orm import relationship
# from database import Base
# from datetime import datetime
# import pytz

# class UserInteraction(Base):
#     __tablename__ = "user_interactions"
    
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
#     user_role = Column(String, nullable=False)
    
#     # Interaction details
#     interaction_type = Column(String, nullable=False)  # 'chat', 'order', 'product_view', etc.
#     content = Column(Text, nullable=False)            # The actual interaction content
    
#     # Context
#     related_data = Column(JSON, nullable=True)        # Store any related IDs or data (order_id, product_id, etc.)
    
#     # Timestamps
#     created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    
#     # Relationships
#     user = relationship("User")

#     __table_args__ = {'extend_existing': True}

# class ChatMessage(Base):
#     __tablename__ = "chat_messages"
    
#     id = Column(Integer, primary_key=True, index=True)
#     interaction_id = Column(Integer, ForeignKey("user_interactions.id", ondelete="CASCADE"), nullable=False)
    
#     role = Column(String, nullable=False)      # 'user' or 'assistant'
#     message = Column(Text, nullable=False)     # The actual message
#     timestamp = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    
#     # Optional feedback
#     is_helpful = Column(Integer, nullable=True)  # Simple rating if provided
    
#     __table_args__ = {'extend_existing': True}

# class OrderInteraction(Base):
#     __tablename__ = "order_interactions"
    
#     id = Column(Integer, primary_key=True, index=True)
#     interaction_id = Column(Integer, ForeignKey("user_interactions.id", ondelete="CASCADE"), nullable=False)
    
#     order_id = Column(Integer, nullable=False)
#     action = Column(String, nullable=False)    # 'create', 'update', 'cancel', etc.
#     details = Column(JSON, nullable=True)      # Order details at time of interaction
#     timestamp = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    
#     __table_args__ = {'extend_existing': True}

# class ProductInteraction(Base):
#     __tablename__ = "product_interactions"
    
#     id = Column(Integer, primary_key=True, index=True)
#     interaction_id = Column(Integer, ForeignKey("user_interactions.id", ondelete="CASCADE"), nullable=False)
    
#     product_id = Column(Integer, nullable=False)
#     action = Column(String, nullable=False)    # 'view', 'rate', 'review', etc.
#     details = Column(JSON, nullable=True)      # Product details at time of interaction
#     timestamp = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    
#     __table_args__ = {'extend_existing': True} 