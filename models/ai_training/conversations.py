# from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Enum as SQLEnum, Text, Float, Boolean
# from sqlalchemy.orm import relationship
# from database import Base
# from datetime import datetime
# import pytz
# from enum import Enum as PyEnum

# class ConversationTypeEnum(PyEnum):
#     CUSTOMER_SUPPORT = "CUSTOMER_SUPPORT"  # For customer questions about products/orders
#     ADMIN_SUPPORT = "ADMIN_SUPPORT"        # For admin/manager questions about system
#     PRODUCT_INQUIRY = "PRODUCT_INQUIRY"    # Specific product-related questions
#     ORDER_SUPPORT = "ORDER_SUPPORT"        # Order-related support
#     TECHNICAL_HELP = "TECHNICAL_HELP"      # Technical/website usage questions

# class ConversationStatusEnum(PyEnum):
#     ONGOING = "ONGOING"
#     RESOLVED = "RESOLVED"
#     NEEDS_FOLLOWUP = "NEEDS_FOLLOWUP"
#     ESCALATED = "ESCALATED"

# class Conversation(Base):
#     __tablename__ = "ai_conversations"
    
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
#     user_role = Column(String, nullable=False)  # Store the role at time of conversation
#     conversation_type = Column(SQLEnum(ConversationTypeEnum), nullable=False)
#     status = Column(SQLEnum(ConversationStatusEnum), default=ConversationStatusEnum.ONGOING)
    
#     # Context information
#     context_data = Column(JSON, nullable=True)  # Store relevant context (product IDs, order IDs, etc.)
#     session_data = Column(JSON, nullable=True)  # Additional session info (browser, device, etc.)
#     language = Column(String, nullable=True)    # Language of conversation
    
#     # Training-specific fields
#     conversation_quality = Column(Integer, nullable=True)  # Overall quality rating (1-5)
#     sentiment_score = Column(Float, nullable=True)        # Sentiment analysis score
#     topics = Column(JSON, nullable=True)                  # List of detected topics
    
#     # Timestamps
#     created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
#     updated_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))
#     resolved_at = Column(DateTime, nullable=True)
    
#     # Relationships
#     messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")
#     user = relationship("User")

#     __table_args__ = {'extend_existing': True}

# class ConversationMessage(Base):
#     __tablename__ = "ai_conversation_messages"
    
#     id = Column(Integer, primary_key=True, index=True)
#     conversation_id = Column(Integer, ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False)
    
#     # Message content
#     role = Column(String, nullable=False)  # 'user', 'assistant', or 'system'
#     content = Column(Text, nullable=False)
#     content_type = Column(String, default='text')  # text, image, file, etc.
    
#     # Training-specific fields
#     is_helpful = Column(Integer, nullable=True)  # User rating of response helpfulness
#     feedback = Column(String, nullable=True)     # User feedback on response
#     response_time = Column(Float, nullable=True) # Time taken to respond (in seconds)
#     confidence_score = Column(Float, nullable=True) # AI confidence in the response
    
#     # Context tracking
#     relevant_entities = Column(JSON, nullable=True)  # Store IDs of relevant products, orders, etc.
#     intent = Column(String, nullable=True)          # Detected user intent
#     sentiment = Column(Float, nullable=True)        # Message sentiment score
    
#     # Timestamps
#     created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    
#     # Relationships
#     conversation = relationship("Conversation", back_populates="messages")

#     __table_args__ = {'extend_existing': True}

# class TrainingExample(Base):
#     __tablename__ = "ai_training_examples"
    
#     id = Column(Integer, primary_key=True, index=True)
#     conversation_id = Column(Integer, ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False)
    
#     # Training data
#     input_text = Column(Text, nullable=False)    # The user's question/input
#     output_text = Column(Text, nullable=False)   # The ideal response
#     context = Column(JSON, nullable=True)        # Relevant context for training
    
#     # Training metadata
#     category = Column(String, nullable=False)    # Category of the training example
#     tags = Column(JSON, nullable=True)          # Tags for filtering/organizing
#     quality_score = Column(Integer, nullable=True)  # Quality rating of this example
#     difficulty_level = Column(Integer, nullable=True)  # Complexity level (1-5)
#     is_validated = Column(Boolean, default=False)     # Whether verified by admin
#     validation_notes = Column(Text, nullable=True)    # Notes from validation
    
#     # Performance metrics
#     success_rate = Column(Float, nullable=True)      # Success rate in training
#     avg_confidence = Column(Float, nullable=True)     # Average confidence score
    
#     # Timestamps
#     created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
#     updated_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))
#     validated_at = Column(DateTime, nullable=True)
    
#     __table_args__ = {'extend_existing': True} 