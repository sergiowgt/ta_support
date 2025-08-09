import os
from dotenv import load_dotenv

load_dotenv()

class GoogleLoginConfig:
    CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    
