from abc import ABC, abstractmethod
from datetime import datetime


class IVerificationRepository(ABC):
    """Porta de persistência do desafio de verificação de posse.

    O consumidor implementa contra a própria entidade/tabela (ex.:
    `contact_verification` no MV). O serviço nunca importa a entidade concreta —
    trabalha por esta porta (duck-typing no objeto retornado), igual o
    GoogleLoginService faz com o user_repository.

    Contrato de unicidade: existe no máximo UM desafio ativo (não verificado)
    por (target, channel). `upsert_pending` substitui o ativo em vez de acumular
    linhas.

    O objeto retornado por `get_active` deve expor os atributos:
    `code_hash: str`, `expires_at: datetime`, `attempts: int`,
    `last_sent_at: datetime | None`.
    """

    @abstractmethod
    async def get_active(self, *, target: str, channel: str):
        """Retorna o desafio ativo (PENDING, não verificado) de (target, channel),
        ou None se não houver."""
        ...

    @abstractmethod
    async def upsert_pending(self, *, target: str, channel: str, code_hash: str,
                             expires_at: datetime, sent_at: datetime):
        """Cria — ou substitui o ativo existente — um desafio PENDING com o
        `code_hash`/`expires_at`/`sent_at` dados, zerando o contador de
        tentativas. Retorna o registro persistido."""
        ...

    @abstractmethod
    async def register_failed_attempt(self, record) -> None:
        """Incrementa o contador de tentativas do registro (código errado)."""
        ...

    @abstractmethod
    async def mark_verified(self, record, *, verified_at: datetime) -> None:
        """Marca o registro como verificado (posse comprovada)."""
        ...
