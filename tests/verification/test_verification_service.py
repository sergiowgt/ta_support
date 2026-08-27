import asyncio
from datetime import datetime, timedelta, timezone

from TA.support.exceptions import BusinessRuleException
from TA.support.i18n.message_provider import MessageProvider
from TA.support.verification import (
    ISender,
    IVerificationRepository,
    VerificationChannel,
    VerificationService,
)

MessageProvider._load_locales()  # carrega o locale builtin (get_message real)

EMAIL = "cidadao@exemplo.com"


class _Record:
    def __init__(self, code_hash, expires_at, sent_at):
        self.code_hash = code_hash
        self.expires_at = expires_at
        self.last_sent_at = sent_at
        self.attempts = 0
        self.verified_at = None


class FakeRepo(IVerificationRepository):
    """Persistência em memória: no máximo 1 ativo por (target, channel)."""

    def __init__(self):
        self.store = {}

    async def get_active(self, *, target, channel):
        rec = self.store.get((target, channel))
        if rec is not None and rec.verified_at is not None:
            return None
        return rec

    async def upsert_pending(self, *, target, channel, code_hash, expires_at, sent_at):
        rec = _Record(code_hash, expires_at, sent_at)
        self.store[(target, channel)] = rec
        return rec

    async def register_failed_attempt(self, record):
        record.attempts += 1

    async def mark_verified(self, record, *, verified_at):
        record.verified_at = verified_at


class FakeSender(ISender):
    def __init__(self):
        self.sent = []

    async def send(self, *, target, channel, code):
        self.sent.append((target, channel, code))


def _svc(**kw):
    return VerificationService("test-secret-pepper", **kw)


def test_start_generates_numeric_code_and_persists_hash_not_code():
    async def run():
        repo, sender = FakeRepo(), FakeSender()
        svc = _svc()
        rec = await svc.start(repo, sender, target=EMAIL, channel=VerificationChannel.EMAIL)
        assert len(sender.sent) == 1
        target, channel, code = sender.sent[0]
        assert channel == "EMAIL"
        assert len(code) == 6 and code.isdigit()
        # persistiu o HASH, nunca o código em claro
        assert rec.code_hash != code
        assert rec.code_hash == svc.hash_code(target=EMAIL, channel="EMAIL", code=code)

    asyncio.run(run())


def test_confirm_success_marks_verified():
    async def run():
        repo, sender = FakeRepo(), FakeSender()
        svc = _svc()
        await svc.start(repo, sender, target=EMAIL, channel="EMAIL")
        code = sender.sent[0][2]
        rec = await svc.confirm(repo, target=EMAIL, channel="EMAIL", code=code)
        assert rec.verified_at is not None

    asyncio.run(run())


def test_confirm_wrong_code_increments_and_raises():
    async def run():
        repo, sender = FakeRepo(), FakeSender()
        svc = _svc()
        await svc.start(repo, sender, target=EMAIL, channel="EMAIL")
        try:
            await svc.confirm(repo, target=EMAIL, channel="EMAIL", code="000000")
            assert False, "código errado deveria levantar"
        except BusinessRuleException:
            pass
        assert repo.store[(EMAIL, "EMAIL")].attempts == 1

    asyncio.run(run())


def test_confirm_expired_raises():
    async def run():
        repo, sender = FakeRepo(), FakeSender()
        svc = _svc()
        await svc.start(repo, sender, target=EMAIL, channel="EMAIL")
        code = sender.sent[0][2]
        repo.store[(EMAIL, "EMAIL")].expires_at = datetime.now(timezone.utc) - timedelta(seconds=5)
        try:
            await svc.confirm(repo, target=EMAIL, channel="EMAIL", code=code)
            assert False, "código expirado deveria levantar"
        except BusinessRuleException:
            pass

    asyncio.run(run())


def test_confirm_blocks_at_max_attempts_before_checking_code():
    async def run():
        repo, sender = FakeRepo(), FakeSender()
        svc = _svc(max_attempts=2)
        await svc.start(repo, sender, target=EMAIL, channel="EMAIL")
        code = sender.sent[0][2]  # código CORRETO
        repo.store[(EMAIL, "EMAIL")].attempts = 2
        try:
            await svc.confirm(repo, target=EMAIL, channel="EMAIL", code=code)
            assert False, "no teto de tentativas deveria travar mesmo com código certo"
        except BusinessRuleException:
            pass

    asyncio.run(run())


def test_resend_cooldown_blocks_immediate_restart():
    async def run():
        repo, sender = FakeRepo(), FakeSender()
        svc = _svc(resend_cooldown_seconds=60)
        await svc.start(repo, sender, target=EMAIL, channel="EMAIL")
        try:
            await svc.start(repo, sender, target=EMAIL, channel="EMAIL")
            assert False, "cooldown deveria bloquear o reenvio imediato"
        except BusinessRuleException:
            pass

    asyncio.run(run())


def test_naive_datetime_from_mysql_does_not_raise_typeerror():
    async def run():
        repo, sender = FakeRepo(), FakeSender()
        svc = _svc()
        await svc.start(repo, sender, target=EMAIL, channel="EMAIL")
        code = sender.sent[0][2]
        # simula o que o MySQL devolve: DATETIME naïve (sem tzinfo)
        rec = repo.store[(EMAIL, "EMAIL")]
        naive_now = datetime.now(timezone.utc).replace(tzinfo=None)
        rec.expires_at = naive_now + timedelta(minutes=5)
        rec.last_sent_at = naive_now
        out = await svc.confirm(repo, target=EMAIL, channel="EMAIL", code=code)
        assert out.verified_at is not None

    asyncio.run(run())
