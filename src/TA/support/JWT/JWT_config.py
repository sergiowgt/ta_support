import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class JWTConfig:
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "vozes")
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    @staticmethod
    def get_expiration_delta() -> timedelta:
        return timedelta(minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES)