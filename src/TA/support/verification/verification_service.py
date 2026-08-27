import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum

from TA.support.exceptions import BusinessRuleException
from TA.support.i18n.message_provider import MessageProvider


class VerificationService:
    """Máquina de verificação de posse de contato (double opt-in por código).

    Agnóstica de canal e de persistência: recebe um `repository`
    (IVerificationRepository) e um `sender` (ISender) por método — espelhando o
    GoogleLoginService, que recebe o user_repository por argumento. Toda a
    política (geração do código, hash, expiração, tentativas, cooldown de
    reenvio) mora aqui e é reusada por qualquer projeto consumidor.

    Segurança: nunca persiste o código em claro — só o HMAC-SHA256 com o
    `secret` do serviço (pepper), amarrado a (channel, target). Comparação em
    tempo constante (`hmac.compare_digest`). O limite de tentativas trava
    brute-force online; o pepper protege o hash em repouso.

    Falhas levantam `BusinessRuleException` — já mapeada a HTTP 400 nos
    consumidores, então não exige exception handler novo.
    """

    def __init__(self, secret: str, *, code_length: int = 6,
                 ttl_seconds: int = 600, max_attempts: int = 5,
                 resend_cooldown_seconds: int = 60):
        if not secret:
            raise ValueError(
                "VerificationService exige um `secret` não vazio (pepper do hash)."
            )
        self._secret = secret
        self._code_length = code_length
        self._ttl_seconds = ttl_seconds
        self._max_attempts = max_attempts
        self._resend_cooldown_seconds = resend_cooldown_seconds

    # ---------- helpers ----------
    @staticmethod
    def _channel_value(channel) -> str:
        return channel.value if isinstance(channel, Enum) else str(channel)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _as_aware_utc(dt: datetime) -> datetime:
        # MySQL devolve DATETIME naïve; tratamos como UTC para comparar sem TypeError.
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def _generate_code(self) -> str:
        upper = 10 ** self._code_length
        return str(secrets.randbelow(upper)).zfill(self._code_length)

    def hash_code(self, *, target: str, channel, code: str) -> str:
        """HMAC-SHA256(secret, "channel:target:code"). Público para o consumidor
        poder reusar exatamente o mesmo cálculo se precisar."""
        msg = f"{self._channel_value(channel)}:{target}:{code}".encode("utf-8")
        return hmac.new(self._secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

    # ---------- API ----------
    async def start(self, repository, sender, *, target: str, channel):
        """Gera um código, persiste o hash e entrega pelo sender. Respeita o
        cooldown de reenvio. Retorna o registro persistido."""
        channel_value = self._channel_value(channel)

        active = await repository.get_active(target=target, channel=channel_value)
        if active is not None:
            last_sent = getattr(active, "last_sent_at", None)
            if last_sent is not None:
                elapsed = (self._now() - self._as_aware_utc(last_sent)).total_seconds()
                if elapsed < self._resend_cooldown_seconds:
                    wait = int(self._resend_cooldown_seconds - elapsed)
                    raise BusinessRuleException(
                        MessageProvider.get_message(
                            "verification.error.resend_cooldown", {"seconds": wait}
                        )
                    )

        code = self._generate_code()
        code_hash = self.hash_code(target=target, channel=channel_value, code=code)
        now = self._now()
        record = await repository.upsert_pending(
            target=target,
            channel=channel_value,
            code_hash=code_hash,
            expires_at=now + timedelta(seconds=self._ttl_seconds),
            sent_at=now,
        )
        await sender.send(target=target, channel=channel_value, code=code)
        return record

    async def confirm(self, repository, *, target: str, channel, code: str):
        """Valida o código digitado pelo usuário. Levanta BusinessRuleException
        (→400) em qualquer falha; em sucesso marca posse comprovada e retorna o
        registro."""
        channel_value = self._channel_value(channel)

        record = await repository.get_active(target=target, channel=channel_value)
        if record is None:
            raise BusinessRuleException(
                MessageProvider.get_message("verification.error.not_found")
            )
        if self._now() > self._as_aware_utc(record.expires_at):
            raise BusinessRuleException(
                MessageProvider.get_message("verification.error.expired")
            )
        if getattr(record, "attempts", 0) >= self._max_attempts:
            raise BusinessRuleException(
                MessageProvider.get_message("verification.error.max_attempts")
            )

        expected = self.hash_code(target=target, channel=channel_value, code=code or "")
        if not hmac.compare_digest(expected, record.code_hash):
            await repository.register_failed_attempt(record)
            raise BusinessRuleException(
                MessageProvider.get_message("verification.error.invalid_code")
            )

        await repository.mark_verified(record, verified_at=self._now())
        return record
