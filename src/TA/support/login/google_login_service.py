from TA.support.i18n.message_provider import MessageProvider
from TA.support.login.Ilogin_repository import ILoginRepository
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from TA.support.exceptions import LoginException

class GoogleLoginService():
    def __init__(self, user_repository: ILoginRepository, google_login_api_key: str):
        self.user_repository = user_repository
        self.google_login_api_key = google_login_api_key

    async def login(self, google_token):
        try:
            idinfo = google_id_token.verify_oauth2_token(google_token, google_requests.Request(), self.google_login_api_key)
            email = idinfo.get("email")
            name = idinfo.get("name")
            if not email or not name:
                raise LoginException("1")
        except Exception as e:
            raise LoginException(str(e))

        user = await self.user_repository.get_by_email(email)
        if not user:
            raise LoginException(MessageProvider.get_message("validation.error.user_not_exists"))

        return {
            "email": email,
            "name": name
        }
