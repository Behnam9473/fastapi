from typing import Optional, Union, Protocol
from sqlalchemy.orm import Session
from models.users.users import User, Admin, Manager, Customer
from utils.auth import verify_password
from utils.exceptions import AuthenticationError

class Authenticator(Protocol):
    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        pass

class UserAuthenticator:
    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            user = db.query(Customer).filter(Customer.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError(message="Invalid username or password")
            
        return user

class ManagerAuthenticator:
    def authenticate(self, db: Session, username: str, password: str) -> Optional[Manager]:
        user = db.query(Manager).filter(Manager.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

class AdminAuthenticator:
    def authenticate(self, db: Session, username: str, password: str) -> Optional[Admin]:
        user = db.query(Admin).filter(Admin.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

# Factory for getting the appropriate authenticator
def get_authenticator(user_type: str) -> Authenticator:
    authenticators = {
        "user": UserAuthenticator(),
        "manager": ManagerAuthenticator(),
        "admin": AdminAuthenticator()
    }
    return authenticators.get(user_type.lower(), UserAuthenticator()) 