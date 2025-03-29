# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from database import get_db
# from models.ai_training.conversations import Conversation, ConversationMessage, TrainingExample
# from schemas.ai_training.conversations import (
#     ConversationUpdate, ConversationResponse,
#     MessageUpdate, MessageResponse,
#     TrainingExampleUpdate, TrainingExampleResponse,
#     ConversationType, ConversationStatus
# )
# from utils.auth import get_current_user
# from models.users.users import RoleEnum
# from services.ai_training_service import AITrainingService
# from datetime import datetime
# import pytz


# router = APIRouter(prefix="/ai-training", tags=["AI Training"])

# # Admin-only endpoints for managing training data
# @router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
# def update_conversation(
#     conversation_id: int,
#     conversation_update: ConversationUpdate,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     """Update conversation metadata (Admin only)"""
#     if current_user.role != RoleEnum.SUPERUSER:
#         raise HTTPException(
#             status_code=403,
#             detail="Only admins can update conversations"
#         )
    
#     conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
#     if not conversation:
#         raise HTTPException(status_code=404, detail="Conversation not found")
    
#     for field, value in conversation_update.dict(exclude_unset=True).items():
#         setattr(conversation, field, value)
    
#     db.commit()
#     db.refresh(conversation)
#     return conversation

# @router.patch("/messages/{message_id}", response_model=MessageResponse)
# def update_message(
#     message_id: int,
#     message_update: MessageUpdate,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     """Update message feedback and analysis (Admin only)"""
#     if current_user.role != RoleEnum.SUPERUSER:
#         raise HTTPException(
#             status_code=403,
#             detail="Only admins can update messages"
#         )
    
#     message = db.query(ConversationMessage).filter(ConversationMessage.id == message_id).first()
#     if not message:
#         raise HTTPException(status_code=404, detail="Message not found")
    
#     for field, value in message_update.dict(exclude_unset=True).items():
#         setattr(message, field, value)
    
#     db.commit()
#     db.refresh(message)
#     return message

# @router.patch("/training-examples/{example_id}", response_model=TrainingExampleResponse)
# def update_training_example(
#     example_id: int,
#     example_update: TrainingExampleUpdate,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     """Update training example (Admin only)"""
#     if current_user.role != RoleEnum.SUPERUSER:
#         raise HTTPException(
#             status_code=403,
#             detail="Only admins can update training examples"
#         )
    
#     example = db.query(TrainingExample).filter(TrainingExample.id == example_id).first()
#     if not example:
#         raise HTTPException(status_code=404, detail="Training example not found")
    
#     for field, value in example_update.dict(exclude_unset=True).items():
#         setattr(example, field, value)
    
#     if example_update.is_validated:
#         example.validated_at = datetime.now(pytz.UTC)
    
#     db.commit()
#     db.refresh(example)
#     return example

# @router.get("/conversations", response_model=List[ConversationResponse])
# def get_conversations(
#     conversation_type: Optional[ConversationType] = None,
#     status: Optional[ConversationStatus] = None,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(10, ge=1, le=100),
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     """Get conversations with optional filtering"""
#     query = db.query(Conversation)
    
#     if conversation_type:
#         query = query.filter(Conversation.conversation_type == conversation_type)
#     if status:
#         query = query.filter(Conversation.status == status)
    
#     # Regular users can only see their own conversations
#     if current_user.role == RoleEnum.CUSTOMER:
#         query = query.filter(Conversation.user_id == current_user.id)
    
#     conversations = query.offset(skip).limit(limit).all()
#     return conversations

# @router.get("/training-examples", response_model=List[TrainingExampleResponse])
# def get_training_examples(
#     category: Optional[str] = None,
#     min_quality: Optional[int] = Query(None, ge=1, le=5),
#     is_validated: Optional[bool] = None,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(10, ge=1, le=100),
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     """Get training examples with optional filtering (Admin only)"""
#     if current_user.role != RoleEnum.SUPERUSER:
#         raise HTTPException(
#             status_code=403,
#             detail="Only admins can access training examples"
#         )
    
#     query = db.query(TrainingExample)
    
#     if category:
#         query = query.filter(TrainingExample.category == category)
#     if min_quality:
#         query = query.filter(TrainingExample.quality_score >= min_quality)
#     if is_validated is not None:
#         query = query.filter(TrainingExample.is_validated == is_validated)
    
#     examples = query.offset(skip).limit(limit).all()
#     return examples

# @router.post("/training-examples/{conversation_id}/auto-create", response_model=Optional[TrainingExampleResponse])
# def auto_create_training_example(
#     conversation_id: int,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     """Automatically create a training example from a conversation (Admin only)"""
#     if current_user.role != RoleEnum.SUPERUSER:
#         raise HTTPException(
#             status_code=403,
#             detail="Only admins can create training examples"
#         )
    
#     ai_service = AITrainingService(db)
#     example = ai_service.auto_create_training_example(conversation_id)
    
#     if not example:
#         raise HTTPException(
#             status_code=400,
#             detail="Conversation is not suitable for creating a training example"
#         )
    
#     return example 