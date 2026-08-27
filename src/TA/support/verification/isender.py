from abc import ABC, abstractmethod


class ISender(ABC):
    """Porta de entrega do código de verificação.

    O projeto consumidor injeta o adapter concreto:
    - e-mail: Resend/SMTP (real);
    - celular: Twilio/Meta WhatsApp (real) ou mock (fase atual do MV);
    - testes: mock em memória.

    Espelha o padrão de porta do módulo `login` (ILoginRepository): o TA declara
    a interface, o consumidor implementa.
    """

    @abstractmethod
    async def send(self, *, target: str, channel: str, code: str) -> None:
        """Entrega `code` ao `target` pelo `channel`.

        Não retorna nada. Deve levantar exceção em falha de entrega (o serviço
        já terá persistido o desafio antes de chamar o sender).
        """
        ...
