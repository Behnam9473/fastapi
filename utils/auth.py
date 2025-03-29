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
    try:
        is_valid = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Password verification result: {is_valid}")
        return is_valid
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
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
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
async def get_current_manager(token: str = Depends(manager_oauth)):
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