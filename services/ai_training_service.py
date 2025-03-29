# from datetime import datetime
# import pytz
# from sqlalchemy.orm import Session
# from models.ai_training.conversations import (
#     Conversation, ConversationMessage, TrainingExample,
#     ConversationTypeEnum, ConversationStatusEnum
# )
# from typing import Dict, Any, Optional, List
# import json
# from textblob import TextBlob  # For basic sentiment analysis

# class AITrainingService:
#     def __init__(self, db: Session):
#         self.db = db

#     def detect_intent(self, text: str) -> str:
#         """Simple intent detection based on keywords"""
#         text = text.lower()
#         if any(word in text for word in ["where", "track", "status", "when"]):
#             return "tracking"
#         elif any(word in text for word in ["how", "what", "explain", "tell"]):
#             return "information"
#         elif any(word in text for word in ["help", "support", "assist"]):
#             return "support"
#         elif any(word in text for word in ["buy", "purchase", "order", "cart"]):
#             return "purchase"
#         return "general"

#     def analyze_sentiment(self, text: str) -> float:
#         """Basic sentiment analysis using TextBlob"""
#         analysis = TextBlob(text)
#         # Convert polarity to range -1 to 1
#         return analysis.sentiment.polarity

#     def detect_topics(self, text: str) -> List[str]:
#         """Simple topic detection based on keywords"""
#         topics = []
#         text = text.lower()
        
#         topic_keywords = {
#             "shipping": ["delivery", "shipping", "track", "arrive"],
#             "product": ["product", "item", "good", "quality"],
#             "payment": ["payment", "price", "cost", "pay"],
#             "technical": ["website", "app", "login", "account"],
#             "support": ["help", "support", "assist", "issue"]
#         }

#         for topic, keywords in topic_keywords.items():
#             if any(keyword in text for keyword in keywords):
#                 topics.append(topic)
        
#         return topics

#     def create_conversation(
#         self,
#         user_id: int,
#         user_role: str,
#         conversation_type: ConversationTypeEnum,
#         context_data: Optional[Dict] = None,
#         session_data: Optional[Dict] = None,
#         language: str = "en"
#     ) -> Conversation:
#         """Automatically create a new conversation with initial analysis"""
#         conversation = Conversation(
#             user_id=user_id,
#             user_role=user_role,
#             conversation_type=conversation_type,
#             context_data=context_data,
#             session_data=session_data,
#             language=language,
#             status=ConversationStatusEnum.ONGOING
#         )
        
#         self.db.add(conversation)
#         self.db.commit()
#         self.db.refresh(conversation)
#         return conversation

#     def add_message(
#         self,
#         conversation_id: int,
#         role: str,
#         content: str,
#         content_type: str = "text",
#         relevant_entities: Optional[Dict] = None,
#         response_start_time: Optional[float] = None
#     ) -> ConversationMessage:
#         """Automatically add a message with analysis"""
#         # Calculate response time if provided
#         response_time = None
#         if response_start_time:
#             response_time = datetime.now(pytz.UTC).timestamp() - response_start_time

#         # Analyze message
#         intent = self.detect_intent(content) if role == "user" else None
#         sentiment = self.analyze_sentiment(content)

#         message = ConversationMessage(
#             conversation_id=conversation_id,
#             role=role,
#             content=content,
#             content_type=content_type,
#             relevant_entities=relevant_entities,
#             intent=intent,
#             sentiment=sentiment,
#             response_time=response_time
#         )

#         self.db.add(message)
#         self.db.commit()
#         self.db.refresh(message)

#         # Update conversation analysis
#         self._update_conversation_analysis(conversation_id)
        
#         return message

#     def _update_conversation_analysis(self, conversation_id: int):
#         """Update conversation-level analysis based on messages"""
#         conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
#         if not conversation:
#             return

#         messages = conversation.messages
#         if not messages:
#             return

#         # Update sentiment score (average of all messages)
#         sentiments = [m.sentiment for m in messages if m.sentiment is not None]
#         if sentiments:
#             conversation.sentiment_score = sum(sentiments) / len(sentiments)

#         # Update topics
#         all_topics = []
#         for message in messages:
#             if message.role == "user":
#                 all_topics.extend(self.detect_topics(message.content))
#         conversation.topics = list(set(all_topics))  # Remove duplicates

#         self.db.commit()

#     def auto_create_training_example(
#         self,
#         conversation_id: int,
#         threshold_quality: float = 0.8
#     ) -> Optional[TrainingExample]:
#         """Automatically create a training example if conversation quality is high enough"""
#         conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
#         if not conversation:
#             return None

#         # Check if conversation is suitable for training
#         if not self._is_suitable_for_training(conversation):
#             return None

#         # Find a good Q&A pair
#         user_messages = [m for m in conversation.messages if m.role == "user"]
#         assistant_messages = [m for m in conversation.messages if m.role == "assistant"]

#         if not user_messages or not assistant_messages:
#             return None

#         # Use the highest rated Q&A pair
#         best_qa_pair = None
#         highest_rating = -1

#         for user_msg in user_messages:
#             for asst_msg in assistant_messages:
#                 if asst_msg.is_helpful and asst_msg.is_helpful > highest_rating:
#                     best_qa_pair = (user_msg, asst_msg)
#                     highest_rating = asst_msg.is_helpful

#         if not best_qa_pair or highest_rating < 4:  # Only use highly rated responses
#             return None

#         user_msg, asst_msg = best_qa_pair

#         # Create training example
#         example = TrainingExample(
#             conversation_id=conversation_id,
#             input_text=user_msg.content,
#             output_text=asst_msg.content,
#             context=conversation.context_data,
#             category=user_msg.intent or "general",
#             tags=conversation.topics,
#             quality_score=highest_rating,
#             difficulty_level=self._calculate_difficulty(user_msg.content),
#             is_validated=False
#         )

#         self.db.add(example)
#         self.db.commit()
#         self.db.refresh(example)
#         return example

#     def _is_suitable_for_training(self, conversation: Conversation) -> bool:
#         """Check if conversation is suitable for training"""
#         if conversation.status != ConversationStatusEnum.RESOLVED:
#             return False

#         if not conversation.messages:
#             return False

#         # Check if there are both user and assistant messages
#         roles = set(m.role for m in conversation.messages)
#         if not {"user", "assistant"}.issubset(roles):
#             return False

#         # Check if there are any helpful ratings
#         has_helpful_rating = any(
#             m.is_helpful is not None and m.is_helpful >= 4
#             for m in conversation.messages
#             if m.role == "assistant"
#         )
#         if not has_helpful_rating:
#             return False

#         return True

#     def _calculate_difficulty(self, text: str) -> int:
#         """Calculate difficulty level of the question (1-5)"""
#         # Simple heuristic based on length and complexity
#         words = text.split()
        
#         # Length-based score
#         length_score = min(len(words) / 10, 2.5)
        
#         # Complexity-based score (presence of technical terms, multiple questions, etc.)
#         complexity_indicators = [
#             "how", "why", "what's the difference", "compare",
#             "explain", "technical", "difference between"
#         ]
#         complexity_score = sum(1 for ind in complexity_indicators if ind in text.lower()) / 2
        
#         total_score = length_score + complexity_score
#         return max(1, min(5, round(total_score))) 