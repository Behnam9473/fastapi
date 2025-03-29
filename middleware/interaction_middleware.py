# from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware
# from services.interaction_logger import InteractionLogger
# from database import get_db
# from utils.auth import get_current_manager as get_current_user_from_request
# import json

# class InteractionMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         # Get database session
#         db = next(get_db())
#         logger = InteractionLogger(db)
        
#         try:
#             # Try to get user info
#             user = await get_current_user_from_request(request)
#             user_id = user.id if user else None
#             user_role = user.role.value if user else "anonymous"
#         except:
#             user_id = None
#             user_role = "anonymous"

#         # Get request path and method
#         path = request.url.path
#         method = request.method

#         # Log based on path patterns
#         try:
#             # For chat endpoints
#             if "/chat" in path:
#                 body = await request.json()
#                 logger.log_chat(
#                     user_id=user_id,
#                     user_role=user_role,
#                     message=body.get("message", ""),
#                     role="user",
#                     related_data={"path": path, "method": method}
#                 )

#             # For order endpoints
#             elif "/order" in path:
#                 if method in ["POST", "PUT", "DELETE"]:
#                     try:
#                         body = await request.json()
#                     except:
#                         body = {}
                    
#                     order_id = int(path.split("/")[-1]) if path.split("/")[-1].isdigit() else None
#                     if order_id:
#                         logger.log_order_interaction(
#                             user_id=user_id,
#                             user_role=user_role,
#                             order_id=order_id,
#                             action=method.lower(),
#                             details=body
#                         )

#             # For product endpoints
#             elif "/products" in path:
#                 product_id = int(path.split("/")[-1]) if path.split("/")[-1].isdigit() else None
#                 if product_id:
#                     try:
#                         body = await request.json() if method in ["POST", "PUT"] else {}
#                     except:
#                         body = {}
                    
#                     logger.log_product_interaction(
#                         user_id=user_id,
#                         user_role=user_role,
#                         product_id=product_id,
#                         action=method.lower(),
#                         details=body
#                     )

#         except Exception as e:
#             # Don't let logging errors affect the main request
#             print(f"Interaction logging error: {str(e)}")

#         # Continue with the request
#         response = await call_next(request)
#         return response 