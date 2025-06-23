import json
from pathlib import Path
from collections import defaultdict

class MessageProvider:
    _instance = None
    _locales = {}
    _current_lang = 'pt_BR'
    _default_lang = 'pt_BR'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_locales()
        return cls._instance

    @classmethod
    def _load_locales(cls, locale_dir: str):
        path = Path(locale_dir)
        
        # Verifica se o diretório existe
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError(f"Directory not found: {locale_dir}")
    
        for lang_file in locale_dir.glob('*.json'):
            with open(lang_file, 'r', encoding='utf-8') as f:
                cls._locales[lang_file.stem] = json.load(f)

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
        # Tenta buscar no idioma atual
        messages = cls._locales.get(cls._current_lang, {})
        message = messages.get(key)
        # Fallback para o idioma padrão
        if message is None:
            messages = cls._locales.get(cls._default_lang, {})
            message = messages.get(key, key)  # Fallback para a chave

        # Interpolação segura
        if params:
            class SafeDict(dict):
                def __missing__(self, k):
                    return '{' + k + '}'
            return message.format_map(SafeDict(params))
        return message