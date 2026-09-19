class Language_Error(Exception): ...


_LANGUAGE = "en"


def get() -> str:
    return _LANGUAGE


def set(lang: str) -> None:
    global _LANGUAGE
    if lang not in supported():
        raise Language_Error(f"Language {lang} not known")
    _LANGUAGE = lang


def cycle():
    global _LANGUAGE
    sup = supported()
    i = sup.index(_LANGUAGE)
    i += 1
    if i >= len(sup):
        i = 0
    _LANGUAGE = sup[i]


# Get supported languages
def supported() -> list[str]:
    return ["en", "de"]
