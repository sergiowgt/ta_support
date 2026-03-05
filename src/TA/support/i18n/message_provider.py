import json
from pathlib import Path

class MessageProvider:
    _instance = None
    _locales = {}
    _current_lang = 'pt_BR'
    _default_lang = 'pt_BR'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def _builtin_path(cls) -> Path:
        # src/TA/support/i18n/message_provider.py
        # → parent = i18n/
        # → parent.parent = support/
        # → / locales
        return Path(__file__).parent.parent / "locales"

    @classmethod
    def _load_locales(cls, *extra_dirs):
        """
        Carrega o locale da biblioteca automaticamente.
        O backend pode passar paths adicionais — o último vence em chaves duplicadas.

        Uso no main.py do backend:
            MessageProvider._load_locales("src/locales")
        """
        all_dirs = [cls._builtin_path(), *[Path(d) for d in extra_dirs]]
        merged = {}
        for path in all_dirs:
            lang_file = path / f"{cls._current_lang}.json"
            if lang_file.exists():
                with open(lang_file, 'r', encoding='utf-8') as f:
                    merged.update(json.load(f))
        cls._locales[cls._current_lang] = merged

    @classmethod
    def set_language(cls, lang: str):
        if lang not in cls._locales:
            raise ValueError(f"Language {lang} not supported")
        cls._current_lang = lang

    @classmethod
    def set_default_language(cls, lang: str):
        if lang not in cls._locales:
            raise ValueError(f"Language {lang} not supported")
        cls._default_lang = lang

    @classmethod
    def get_message(cls, key: str, params: dict = None) -> str:
        messages = cls._locales.get(cls._current_lang, {})
        message = messages.get(key)
        if message is None:
            messages = cls._locales.get(cls._default_lang, {})
            message = messages.get(key, key)
        if params:
            class SafeDict(dict):
                def __missing__(self, k):
                    return '{' + k + '}'
            return message.format_map(SafeDict(params))
        return message