from datetime import datetime, timedelta, timezone
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from config import settings 

# Configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
manager_oauth = OAuth2PasswordBearer(tokenUrl="/auth/sellerlogin")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Add logging configuration
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

def verify_password(plain_password, hashed_password):
    """
    Verify if the plain password matches the hashed password.
    
    Args:
        plain_password (str): The password in plain text
        hashed_password (str): The hashed password to compare against
    
    Returns:
        bool: True if passwords match, False otherwise
    """
    try:
        is_valid = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Password verification result: {is_valid}")
        return is_valid
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False

def get_password_hash(password):
    """
    Generate a hash for the given password.
    
    Args:
        password (str): The password to hash
    
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT access token.
    
    Args:
        data (dict): The data to encode in the token, must contain 'sub', 'id', and 'role'
        expires_delta (timedelta, optional): Custom expiration time for the token
    
    Returns:
        str: The encoded JWT token
    
    Raises:
        HTTPException: If required fields are missing
    """
    required_fields = ["sub", "id", "role"]
    for field in required_fields:
        if field not in data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Missing required field: {field}"
            )
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"Token created successfully for user: {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation error: {str(e)}")
        raise

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current user from the JWT token.
    
    Args:
        token (str): The JWT token from the request
    
    Returns:
        dict: User information including username, tenant_id, user_id, and role
    
    Raises:
        HTTPException: If token is invalid or credentials cannot be validated
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        tenant_id: str = payload.get("tenant_id")
        role: bool = payload.get("role")
        
        if username is None or user_id is None: 
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"username": username, 'tenant_id': tenant_id, "user_id": user_id, 'role': role}

#======== Manager and Admin Registration =========
def verify_access_token(token: str):
    """
    Verify and decode a JWT token.
    
    Args:
        token (str): The JWT token to verify
    
    Returns:
        dict: The decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
async def get_current_manager(token: str = Depends(manager_oauth)):
    """
    Get the current manager from the JWT token.
    
    Args:
        token (str): The JWT token from the request
    
    Returns:
        dict: Manager information including username, tenant_id, user_id, and role
    
    Raises:
        HTTPException: If token is invalid or credentials cannot be validated
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        tenant_id: str = payload.get("tenant_id")
        role: bool = payload.get("role")
        
        if username is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"username": username, 'tenant_id': tenant_id, "user_id": user_id, 'role': role}