# from pydantic import BaseModel, Field, confloat
# from typing import Optional, List, Dict, Any
# from datetime import datetime
# from enum import Enum

# class ConversationType(str, Enum):
#     CUSTOMER_SUPPORT = "CUSTOMER_SUPPORT"
#     ADMIN_SUPPORT = "ADMIN_SUPPORT"
#     PRODUCT_INQUIRY = "PRODUCT_INQUIRY"
#     ORDER_SUPPORT = "ORDER_SUPPORT"
#     TECHNICAL_HELP = "TECHNICAL_HELP"

# class ConversationStatus(str, Enum):
#     ONGOING = "ONGOING"
#     RESOLVED = "RESOLVED"
#     NEEDS_FOLLOWUP = "NEEDS_FOLLOWUP"
#     ESCALATED = "ESCALATED"

# class MessageBase(BaseModel):
#     role: str = Field(..., description="Role of the message sender (user/assistant/system)")
#     content: str = Field(..., description="Content of the message")
#     content_type: str = Field(default="text", description="Type of content (text, image, file)")
#     relevant_entities: Optional[Dict[str, Any]] = Field(None, description="IDs of relevant entities")
#     intent: Optional[str] = Field(None, description="Detected user intent")

# class MessageCreate(MessageBase):
#     pass

# class MessageUpdate(BaseModel):
#     is_helpful: Optional[int] = Field(None, ge=1, le=5, description="User rating of response helpfulness (1-5)")
#     feedback: Optional[str] = Field(None, description="User feedback on the response")
#     confidence_score: Optional[float] = Field(None, ge=0, le=1, description="AI confidence in the response")
#     sentiment: Optional[float] = Field(None, ge=-1, le=1, description="Message sentiment score")

# class MessageResponse(MessageBase):
#     id: int
#     conversation_id: int
#     is_helpful: Optional[int]
#     feedback: Optional[str]
#     response_time: Optional[float]
#     confidence_score: Optional[float]
#     sentiment: Optional[float]
#     created_at: datetime

#     class Config:
#         from_attributes = True

# class ConversationBase(BaseModel):
#     conversation_type: ConversationType
#     context_data: Optional[Dict[str, Any]] = Field(None, description="Relevant context information")
#     session_data: Optional[Dict[str, Any]] = Field(None, description="Session information")
#     language: Optional[str] = Field(None, description="Language of conversation")

# class ConversationCreate(ConversationBase):
#     pass

# class ConversationUpdate(BaseModel):
#     status: Optional[ConversationStatus]
#     context_data: Optional[Dict[str, Any]]
#     session_data: Optional[Dict[str, Any]]
#     conversation_quality: Optional[int] = Field(None, ge=1, le=5, description="Overall quality rating (1-5)")
#     sentiment_score: Optional[float] = Field(None, ge=-1, le=1, description="Overall sentiment score")
#     topics: Optional[List[str]] = Field(None, description="List of detected topics")

# class ConversationResponse(ConversationBase):
#     id: int
#     user_id: Optional[int]
#     user_role: str
#     status: ConversationStatus
#     conversation_quality: Optional[int]
#     sentiment_score: Optional[float]
#     topics: Optional[List[str]]
#     messages: List[MessageResponse]
#     created_at: datetime
#     updated_at: datetime
#     resolved_at: Optional[datetime]

#     class Config:
#         from_attributes = True

# class TrainingExampleBase(BaseModel):
#     input_text: str = Field(..., description="The user's question/input")
#     output_text: str = Field(..., description="The ideal response")
#     context: Optional[Dict[str, Any]] = Field(None, description="Relevant context for training")
#     category: str = Field(..., description="Category of the training example")
#     tags: Optional[List[str]] = Field(None, description="Tags for filtering/organizing")
#     difficulty_level: Optional[int] = Field(None, ge=1, le=5, description="Complexity level (1-5)")

# class TrainingExampleCreate(TrainingExampleBase):
#     conversation_id: int

# class TrainingExampleUpdate(BaseModel):
#     input_text: Optional[str]
#     output_text: Optional[str]
#     context: Optional[Dict[str, Any]]
#     category: Optional[str]
#     tags: Optional[List[str]]
#     quality_score: Optional[int] = Field(None, ge=1, le=5, description="Quality rating (1-5)")
#     difficulty_level: Optional[int] = Field(None, ge=1, le=5, description="Complexity level (1-5)")
#     validation_notes: Optional[str] = Field(None, description="Notes from validation")
#     is_validated: Optional[bool] = Field(None, description="Whether verified by admin")

# class TrainingExampleResponse(TrainingExampleBase):
#     id: int
#     conversation_id: int
#     quality_score: Optional[int]
#     is_validated: bool
#     validation_notes: Optional[str]
#     success_rate: Optional[float]
#     avg_confidence: Optional[float]
#     created_at: datetime
#     updated_at: datetime
#     validated_at: Optional[datetime]

#     class Config:
#         from_attributes = True 