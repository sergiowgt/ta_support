from TA.support.i18n.message_provider import MessageProvider
from TA.support.login.Ilogin_repository import ILoginRepository
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from TA.support.exceptions import LoginException

# google_login_service.py — lógica de verificação centralizada
class GoogleLoginService:
    _CLOCK_SKEW = 30
    
    def __init__(self, google_login_api_key: str):
        self.google_login_api_key: str = google_login_api_key 

    def _verify_token(self, google_token: str) -> dict:
        if not google_token:
            raise LoginException(
                MessageProvider.get_message("auth.error.google_token_empty")
            )
        try:
            idinfo = google_id_token.verify_oauth2_token(google_token,
            google_requests.Request(),
            self.google_login_api_key,
            clock_skew_in_seconds=self._CLOCK_SKEW)
        except Exception as exc:
            raise LoginException(
                MessageProvider.get_message(
                    "auth.error.google_token_invalid", {"reason": str(exc)}
                )
            ) from exc

        if not idinfo.get("email") or not idinfo.get("name"):
            raise LoginException(
                MessageProvider.get_message("auth.error.google_token_missing_claims")
            )
        return idinfo

    async def login(self, user_repository, google_token):
        info = self._verify_token(google_token)
        user = await user_repository.get_by_email(info["email"])
        if not user:
            raise LoginException(
                MessageProvider.get_message("auth.error.user_not_exists")
            )
        return user

    async def validate(self, google_token: str) -> dict:
        return self._verify_token(google_token)

