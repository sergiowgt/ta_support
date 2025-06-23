import jwt
from datetime import datetime
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from .JWT_config import JWTConfig

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

class JWTHandler:
    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + JWTConfig.get_expiration_delta()
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWTConfig.SECRET_KEY, algorithm=JWTConfig.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, JWTConfig.SECRET_KEY, algorithms=[JWTConfig.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )

    @staticmethod
    async def verify_token(token: str = Depends(oauth2_scheme)) -> str:
        payload = JWTHandler.decode_token(token)
        user_id = payload.get("sub")  # Obtém o identificador do usuário (sub)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing 'sub' field",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user_id  # Retorna o ID ou email do usuário autenticado
