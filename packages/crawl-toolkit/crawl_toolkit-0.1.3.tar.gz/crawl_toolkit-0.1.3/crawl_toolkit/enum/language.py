from enum import Enum
from typing import Optional

class Language(Enum):
    ENGLISH = "english"
    POLISH = "polish"
    GERMAN = "german"
    FRENCH = "french"
    SPANISH = "spanish"
    ITALIAN = "italian"
    UKRAINIAN = "ukrainian"
    CZECH = "czech"
    PORTUGUESE = "portuguese"
    CROATIAN = "croatian"
    SLOVAK = "slovak"
    DUTCH = "dutch"
    RUSSIAN = "russian"
    HUNGARIAN = "hungarian"

    def get_country_code(self) -> str:
        country_codes = {
            Language.ENGLISH: "us",
            Language.POLISH: "pl",
            Language.GERMAN: "de",
            Language.FRENCH: "fr",
            Language.SPANISH: "es",
            Language.ITALIAN: "it",
            Language.UKRAINIAN: "ua",
            Language.CZECH: "cz",
            Language.PORTUGUESE: "pt",
            Language.CROATIAN: "hr",
            Language.SLOVAK: "sk",
            Language.DUTCH: "nl",
            Language.RUSSIAN: "ru",
            Language.HUNGARIAN: "hu",
        }
        return country_codes[self]

    @classmethod
    def from_country_code(cls, code: str) -> Optional["Language"]:
        code = code.lower()
        code_map = {
            "us": cls.ENGLISH,
            "pl": cls.POLISH,
            "de": cls.GERMAN,
            "fr": cls.FRENCH,
            "es": cls.SPANISH,
            "it": cls.ITALIAN,
            "ua": cls.UKRAINIAN,
            "cz": cls.CZECH,
            "pt": cls.PORTUGUESE,
            "hr": cls.CROATIAN,
            "sk": cls.SLOVAK,
            "nl": cls.DUTCH,
            "ru": cls.RUSSIAN,
            "hu": cls.HUNGARIAN,
        }
        return code_map.get(code, None)

    @staticmethod
    def get_available_languages() -> list[str]:
        return [lang.value for lang in Language]

    def map_forbidden_lang_to_default(self) -> "Language":
        if self == Language.RUSSIAN:
            return Language.ENGLISH
        return self
