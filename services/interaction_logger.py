# from sqlalchemy.orm import Session
# from models.ai_training.interactions import (
#     UserInteraction, ChatMessage, OrderInteraction, ProductInteraction
# )
# from typing import Dict, Any, Optional
# from datetime import datetime
# import json

# class InteractionLogger:
#     def __init__(self, db: Session):
#         self.db = db

#     def log_chat(self, user_id: int, user_role: str, message: str, role: str, 
#                  related_data: Optional[Dict] = None) -> ChatMessage:
#         """Log a chat message"""
#         # Create main interaction record
#         interaction = UserInteraction(
#             user_id=user_id,
#             user_role=user_role,
#             interaction_type="chat",
#             content=message,
#             related_data=related_data
#         )
#         self.db.add(interaction)
#         self.db.flush()  # Get the ID without committing

#         # Create chat message record
#         chat_message = ChatMessage(
#             interaction_id=interaction.id,
#             role=role,
#             message=message
#         )
#         self.db.add(chat_message)
#         self.db.commit()
#         return chat_message

#     def log_order_interaction(self, user_id: int, user_role: str, order_id: int, 
#                             action: str, details: Dict) -> OrderInteraction:
#         """Log an order-related interaction"""
#         # Create main interaction record
#         interaction = UserInteraction(
#             user_id=user_id,
#             user_role=user_role,
#             interaction_type="order",
#             content=f"Order {order_id}: {action}",
#             related_data={"order_id": order_id}
#         )
#         self.db.add(interaction)
#         self.db.flush()

#         # Create order interaction record
#         order_interaction = OrderInteraction(
#             interaction_id=interaction.id,
#             order_id=order_id,
#             action=action,
#             details=details
#         )
#         self.db.add(order_interaction)
#         self.db.commit()
#         return order_interaction

#     def log_product_interaction(self, user_id: int, user_role: str, product_id: int,
#                               action: str, details: Optional[Dict] = None) -> ProductInteraction:
#         """Log a product-related interaction"""
#         # Create main interaction record
#         interaction = UserInteraction(
#             user_id=user_id,
#             user_role=user_role,
#             interaction_type="product",
#             content=f"Product {product_id}: {action}",
#             related_data={"product_id": product_id}
#         )
#         self.db.add(interaction)
#         self.db.flush()

#         # Create product interaction record
#         product_interaction = ProductInteraction(
#             interaction_id=interaction.id,
#             product_id=product_id,
#             action=action,
#             details=details
#         )
#         self.db.add(product_interaction)
#         self.db.commit()
#         return product_interaction

#     def update_chat_feedback(self, chat_message_id: int, is_helpful: int) -> bool:
#         """Update the helpfulness rating of a chat message"""
#         message = self.db.query(ChatMessage).filter(ChatMessage.id == chat_message_id).first()
#         if not message:
#             return False
        
#         message.is_helpful = is_helpful
#         self.db.commit()
#         return True

#     def get_user_history(self, user_id: int, interaction_type: Optional[str] = None,
#                         limit: int = 100) -> list:
#         """Get user's interaction history"""
#         query = self.db.query(UserInteraction).filter(UserInteraction.user_id == user_id)
#         if interaction_type:
#             query = query.filter(UserInteraction.interaction_type == interaction_type)
        
#         return query.order_by(UserInteraction.created_at.desc()).limit(limit).all()

#     def get_product_interactions(self, product_id: int, action: Optional[str] = None,
#                                limit: int = 100) -> list:
#         """Get all interactions for a specific product"""
#         query = self.db.query(ProductInteraction).filter(ProductInteraction.product_id == product_id)
#         if action:
#             query = query.filter(ProductInteraction.action == action)
        
#         return query.order_by(ProductInteraction.timestamp.desc()).limit(limit).all()

#     def get_order_interactions(self, order_id: int, limit: int = 100) -> list:
#         """Get all interactions for a specific order"""
#         return self.db.query(OrderInteraction)\
#             .filter(OrderInteraction.order_id == order_id)\
#             .order_by(OrderInteraction.timestamp.desc())\
#             .limit(limit)\
#             .all() 