"""TA.support.testing — codegen de Camada 0 (Testes de Invariância) — DL-012.

API pública:
    from TA.support.testing import generate_invariants_file
    content: str = generate_invariants_file(MyEntityClass)

CLI:
    python -m TA.support.testing.codegen <module>:<EntityCls>
"""
from TA.support.testing.codegen import generate_invariants_file

__all__ = ['generate_invariants_file']
