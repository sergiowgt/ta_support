"""Regenera (ou verifica) o bloco AUTO-GENERATED dos arquivos de invariância.

Compara apenas o bloco delimitado por marcadores — o bloco CUSTOM (invariantes
cross-campo escritas manualmente) é preservado em atualizações e ignorado em
comparações.

Uso — verificar (modo CI):
    python -m TA.support.testing.regenerate --check \\
        src.domain.entities.tenant:Tenant \\
        tests/unit/domain/test_tenant_invariants.py

Uso — atualizar em-place (preserva CUSTOM):
    python -m TA.support.testing.regenerate \\
        src.domain.entities.tenant:Tenant \\
        tests/unit/domain/test_tenant_invariants.py

Exit codes:
    0  — em sync (--check) ou atualizado com sucesso
    1  — fora de sync (--check) ou erro de importação / leitura / escrita
    2  — uso incorreto (args inválidos)
"""
import re
import sys
from importlib import import_module
from pathlib import Path
from typing import Optional

from TA.support.testing.codegen import generate_invariants_file

_AUTO_START = re.compile(
    r"# === AUTO-GENERATED START[^\n]*\n", re.MULTILINE
)
_AUTO_END = "# === AUTO-GENERATED END ==="

_CUSTOM_START = "# === CUSTOM START"
_CUSTOM_END = "# === CUSTOM END ==="


def _extract_auto_block(content: str) -> Optional[str]:
    """Extrai o conteúdo entre os marcadores AUTO-GENERATED (inclusive)."""
    m = _AUTO_START.search(content)
    if not m:
        return None
    start = m.start()
    end = content.find(_AUTO_END, m.end())
    if end == -1:
        return None
    return content[start : end + len(_AUTO_END)]


def _extract_custom_block(content: str) -> Optional[str]:
    """Extrai o conteúdo entre os marcadores CUSTOM (inclusive)."""
    start = content.find(_CUSTOM_START)
    if start == -1:
        return None
    end = content.find(_CUSTOM_END, start)
    if end == -1:
        return None
    return content[start : end + len(_CUSTOM_END)]


def _load_entity(spec: str):
    """Carrega classe a partir de 'module.path:ClassName'."""
    if ":" not in spec:
        sys.stderr.write(
            f"Formato inválido '{spec}' — esperado '<módulo>:<Classe>'\n"
        )
        sys.exit(2)
    module_path, class_name = spec.split(":", 1)
    try:
        module = import_module(module_path)
    except ImportError as exc:
        sys.stderr.write(f"Erro ao importar '{module_path}': {exc}\n")
        sys.exit(1)
    if not hasattr(module, class_name):
        sys.stderr.write(
            f"Classe '{class_name}' não encontrada em '{module_path}'\n"
        )
        sys.exit(1)
    return getattr(module, class_name)


def check(entity_spec: str, test_file: str) -> int:
    """Verifica se o arquivo está em sync com os metadados atuais da entity.

    Retorna 0 se em sync, 1 se fora de sync.
    """
    entity_cls = _load_entity(entity_spec)
    path = Path(test_file)

    if not path.exists():
        sys.stderr.write(
            f"FORA DE SYNC  {test_file}\n"
            f"  Arquivo não encontrado — gere com:\n"
            f"    python -m TA.support.testing.codegen {entity_spec} > {test_file}\n"
        )
        return 1

    existing = path.read_text(encoding="utf-8")
    existing_auto = _extract_auto_block(existing)
    if existing_auto is None:
        sys.stderr.write(
            f"AVISO  {test_file}\n"
            f"  Marcador AUTO-GENERATED não encontrado — arquivo criado fora do codegen?\n"
        )
        return 1

    fresh = generate_invariants_file(entity_cls)
    fresh_auto = _extract_auto_block(fresh)
    if fresh_auto is None:
        sys.stderr.write("Erro interno: codegen não gerou marcador AUTO-GENERATED\n")
        return 1

    # Normalizar versão no marcador START pra não falhar só por bump de versão
    def _strip_version(block: str) -> str:
        return re.sub(
            r"(# === AUTO-GENERATED START)[^\n]*", r"\1", block
        )

    if _strip_version(existing_auto) == _strip_version(fresh_auto):
        print(f"OK     {test_file}")
        return 0

    sys.stderr.write(
        f"FORA DE SYNC  {test_file}\n"
        f"  Metadados da entity mudaram desde a última geração.\n"
        f"  Regenere com:\n"
        f"    python -m TA.support.testing.regenerate {entity_spec} {test_file}\n"
    )
    return 1


def update(entity_spec: str, test_file: str) -> int:
    """Atualiza o bloco AUTO-GENERATED no arquivo, preservando o bloco CUSTOM.

    Se o arquivo não existir, gera do zero.
    Retorna 0 em sucesso, 1 em erro.
    """
    entity_cls = _load_entity(entity_spec)
    path = Path(test_file)
    fresh = generate_invariants_file(entity_cls)

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fresh, encoding="utf-8")
        print(f"CRIADO  {test_file}")
        return 0

    existing = path.read_text(encoding="utf-8")
    custom_block = _extract_custom_block(existing)

    fresh_auto = _extract_auto_block(fresh)
    if fresh_auto is None:
        sys.stderr.write("Erro interno: codegen não gerou marcador AUTO-GENERATED\n")
        return 1

    existing_auto = _extract_auto_block(existing)
    if existing_auto is None:
        # Arquivo sem marcadores — substituir tudo
        path.write_text(fresh, encoding="utf-8")
        print(f"ATUALIZADO (sem marcadores anteriores)  {test_file}")
        return 0

    # Substituir só o bloco AUTO-GENERATED, preservar CUSTOM
    new_content = existing[: existing.find(existing_auto)] + fresh_auto

    if custom_block:
        new_content += "\n\n\n" + custom_block + "\n"
    else:
        # Pegar CUSTOM do arquivo fresh (bloco vazio com comentário guia)
        fresh_custom = _extract_custom_block(fresh)
        if fresh_custom:
            new_content += "\n\n\n" + fresh_custom + "\n"

    path.write_text(new_content, encoding="utf-8")
    print(f"ATUALIZADO  {test_file}")
    return 0


def main():
    args = sys.argv[1:]
    check_mode = "--check" in args
    args = [a for a in args if a != "--check"]

    if len(args) != 2:
        sys.stderr.write(
            "Uso:\n"
            "  python -m TA.support.testing.regenerate [--check] "
            "<módulo>:<Classe> <test_file>\n\n"
            "Exemplos:\n"
            "  python -m TA.support.testing.regenerate --check \\\n"
            "      src.domain.entities.tenant:Tenant \\\n"
            "      tests/unit/domain/test_tenant_invariants.py\n\n"
            "  python -m TA.support.testing.regenerate \\\n"
            "      src.domain.entities.tenant:Tenant \\\n"
            "      tests/unit/domain/test_tenant_invariants.py\n"
        )
        sys.exit(2)

    entity_spec, test_file = args[0], args[1]
    if check_mode:
        sys.exit(check(entity_spec, test_file))
    else:
        sys.exit(update(entity_spec, test_file))


if __name__ == "__main__":
    main()
