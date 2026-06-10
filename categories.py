"""
Extension-to-category mapping with i18n support.
Category names are automatically translated based on the system locale.
All keys are stored in lowercase; lookup is done with .lower() so the
match is case-insensitive on Windows, Linux and macOS.
"""

from __future__ import annotations

import locale

# Internal canonical keys (never change these)
_DOCUMENTS  = "Documents"
_IMAGES     = "Images"
_VIDEOS     = "Videos"
_AUDIO      = "Audio"
_ARCHIVES   = "Archives"
_INSTALLERS = "Installers"
_CODE       = "Code"
_OTHER      = "Other"

# Translations: canonical key -> {lang_prefix -> localized name}
_TRANSLATIONS: dict[str, dict[str, str]] = {
    _DOCUMENTS: {
        "en": "Documents",
        "es": "Documentos",
        "fr": "Documents",
        "de": "Dokumente",
        "it": "Documenti",
        "pt": "Documentos",
        "ru": "Документы",
        "zh": "文档",
        "ja": "ドキュメント",
        "ko": "문서",
        "nl": "Documenten",
        "pl": "Dokumenty",
        "tr": "Belgeler",
        "ar": "مستندات",
    },
    _IMAGES: {
        "en": "Images",
        "es": "Imágenes",
        "fr": "Images",
        "de": "Bilder",
        "it": "Immagini",
        "pt": "Imagens",
        "ru": "Изображения",
        "zh": "图片",
        "ja": "画像",
        "ko": "이미지",
        "nl": "Afbeeldingen",
        "pl": "Obrazy",
        "tr": "Görseller",
        "ar": "صور",
    },
    _VIDEOS: {
        "en": "Videos",
        "es": "Videos",
        "fr": "Vidéos",
        "de": "Videos",
        "it": "Video",
        "pt": "Vídeos",
        "ru": "Видео",
        "zh": "视频",
        "ja": "動画",
        "ko": "동영상",
        "nl": "Video's",
        "pl": "Wideo",
        "tr": "Videolar",
        "ar": "مقاطع فيديو",
    },
    _AUDIO: {
        "en": "Audio",
        "es": "Audio",
        "fr": "Audio",
        "de": "Audio",
        "it": "Audio",
        "pt": "Áudio",
        "ru": "Аудио",
        "zh": "音频",
        "ja": "オーディオ",
        "ko": "오디오",
        "nl": "Audio",
        "pl": "Audio",
        "tr": "Ses",
        "ar": "صوت",
    },
    _ARCHIVES: {
        "en": "Archives",
        "es": "Archivos comprimidos",
        "fr": "Archives",
        "de": "Archive",
        "it": "Archivi",
        "pt": "Arquivos compactados",
        "ru": "Архивы",
        "zh": "压缩文件",
        "ja": "アーカイブ",
        "ko": "압축파일",
        "nl": "Archieven",
        "pl": "Archiwa",
        "tr": "Arşivler",
        "ar": "ملفات مضغوطة",
    },
    _INSTALLERS: {
        "en": "Installers",
        "es": "Instaladores",
        "fr": "Installateurs",
        "de": "Installationsdateien",
        "it": "Programmi di installazione",
        "pt": "Instaladores",
        "ru": "Установщики",
        "zh": "安装程序",
        "ja": "インストーラー",
        "ko": "설치 파일",
        "nl": "Installatieprogramma's",
        "pl": "Instalatory",
        "tr": "Yükleyiciler",
        "ar": "برامج التثبيت",
    },
    _CODE: {
        "en": "Code",
        "es": "Código",
        "fr": "Code",
        "de": "Code",
        "it": "Codice",
        "pt": "Código",
        "ru": "Код",
        "zh": "代码",
        "ja": "コード",
        "ko": "코드",
        "nl": "Code",
        "pl": "Kod",
        "tr": "Kod",
        "ar": "كود",
    },
    _OTHER: {
        "en": "Other",
        "es": "Otros",
        "fr": "Autres",
        "de": "Sonstiges",
        "it": "Altro",
        "pt": "Outros",
        "ru": "Другое",
        "zh": "其他",
        "ja": "その他",
        "ko": "기타",
        "nl": "Overig",
        "pl": "Inne",
        "tr": "Diğer",
        "ar": "أخرى",
    },
}


def _detect_lang() -> str:
    """Return a 2-letter language code based on the system locale.

    Checks (in order): locale.getlocale(), LANG, LANGUAGE, LC_ALL env vars.
    """
    import os
    try:
        lang = locale.getlocale()[0] or ""
        if lang and lang.lower() not in ("c", "posix"):
            return lang[:2].lower()
    except Exception:
        pass

    for var in ("LANG", "LANGUAGE", "LC_ALL", "LC_MESSAGES"):
        val = os.environ.get(var, "")
        if val and val.lower() not in ("c", "posix", ""):
            return val[:2].lower()

    return "en"


def _localized(canonical: str, lang: str) -> str:
    """Return the localized name for a canonical category key."""
    return _TRANSLATIONS.get(canonical, {}).get(lang) \
        or _TRANSLATIONS.get(canonical, {}).get("en") \
        or canonical


# Detect once at import time (can be overridden for testing)
LANG: str = _detect_lang()

# Build the public CATEGORIES dict with localized names as keys
def _build_categories(lang: str) -> dict[str, set[str]]:
    return {
        _localized(_DOCUMENTS, lang): {
            ".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".md",
            ".xls", ".xlsx", ".ods", ".csv",
            ".ppt", ".pptx", ".odp",
            ".epub", ".mobi", ".azw", ".azw3",
            ".pages", ".numbers", ".key",
        },
        _localized(_IMAGES, lang): {
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
            ".svg", ".tif", ".tiff", ".ico", ".heic", ".heif",
            ".raw", ".psd", ".ai", ".eps",
        },
        _localized(_VIDEOS, lang): {
            ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm",
            ".m4v", ".mpg", ".mpeg", ".3gp", ".vob", ".ogv",
        },
        _localized(_AUDIO, lang): {
            ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a",
            ".opus", ".aiff", ".alac",
        },
        _localized(_ARCHIVES, lang): {
            ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
            ".tgz", ".tbz2", ".txz", ".iso",
        },
        _localized(_INSTALLERS, lang): {
            ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm",
            ".appimage", ".snap", ".apk", ".jar",
        },
        _localized(_CODE, lang): {
            ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss",
            ".json", ".xml", ".yml", ".yaml", ".toml", ".ini", ".cfg",
            ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd",
            ".c", ".cpp", ".h", ".hpp", ".java", ".kt", ".go", ".rs",
            ".rb", ".php", ".sql", ".ipynb", ".r", ".lua", ".swift",
        },
    }


CATEGORIES: dict[str, set[str]] = _build_categories(LANG)
FALLBACK_CATEGORY: str = _localized(_OTHER, LANG)


def get_category(extension: str, custom: dict | None = None) -> str:
    """Return the localized category name for an extension (dot included).

    If ``custom`` is provided and the extension appears in it, that category
    is used. Otherwise it falls back to ``CATEGORIES``. Unknown extensions
    return ``FALLBACK_CATEGORY``.
    """
    ext = (extension or "").lower()
    if not ext:
        return FALLBACK_CATEGORY

    if custom and ext in custom:
        return custom[ext]

    for category, exts in CATEGORIES.items():
        if ext in exts:
            return category
    return FALLBACK_CATEGORY