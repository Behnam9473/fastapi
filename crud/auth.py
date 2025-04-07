from typing import Optional, Union, Protocol
from sqlalchemy.orm import Session
from models.users.users import User, Admin, Manager, Customer
from utils.auth import verify_password
from utils.exceptions import AuthenticationError

class Authenticator(Protocol):
    """Protocol defining the interface for authentication classes.
    
    All authenticator classes must implement the authenticate() method.
    """
    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user.
        
        Args:
            db: SQLAlchemy database session
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        pass

class UserAuthenticator:
    """Authenticator for regular users and customers."""
    
    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a regular user or customer.
        
        Args:
            db: SQLAlchemy database session
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            User object if authentication succeeds
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            user = db.query(Customer).filter(Customer.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError(message="Invalid username or password")
            
        return user

class ManagerAuthenticator:
    """Authenticator for manager users."""
    
    def authenticate(self, db: Session, username: str, password: str) -> Optional[Manager]:
        """Authenticate a manager user.
        
        Args:
            db: SQLAlchemy database session
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            Manager object if authentication succeeds, None otherwise
        """
        user = db.query(Manager).filter(Manager.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

class AdminAuthenticator:
    """Authenticator for admin users."""
    
    def authenticate(self, db: Session, username: str, password: str) -> Optional[Admin]:
        """Authenticate an admin user.
        
        Args:
            db: SQLAlchemy database session
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            Admin object if authentication succeeds, None otherwise
        """
        user = db.query(Admin).filter(Admin.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

def get_authenticator(user_type: str) -> Authenticator:
    """Factory function to get the appropriate authenticator based on user type.
    
    Args:
        user_type: Type of user ('user', 'manager', or 'admin')
        
    Returns:
        Authenticator instance for the specified user type
        Defaults to UserAuthenticator if type is not recognized
    """
    authenticators = {
        "user": UserAuthenticator(),
        "manager": ManagerAuthenticator(),
        "admin": AdminAuthenticator()
    }
    return authenticators.get(user_type.lower(), UserAuthenticator())