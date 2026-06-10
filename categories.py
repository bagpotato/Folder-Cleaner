"""
Extension-to-category mapping.
All keys are stored in lowercase; lookup is done with .lower() so the
match is case-insensitive on Windows, Linux and macOS.
"""

CATEGORIES = {
    "Documents": {
        ".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".md",
        ".xls", ".xlsx", ".ods", ".csv",
        ".ppt", ".pptx", ".odp",
        ".epub", ".mobi", ".azw", ".azw3",
        ".pages", ".numbers", ".key",
    },
    "Images": {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
        ".svg", ".tif", ".tiff", ".ico", ".heic", ".heif",
        ".raw", ".psd", ".ai", ".eps",
    },
    "Videos": {
        ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm",
        ".m4v", ".mpg", ".mpeg", ".3gp", ".vob", ".ogv",
    },
    "Audio": {
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a",
        ".opus", ".aiff", ".alac",
    },
    "Archives": {
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
        ".tgz", ".tbz2", ".txz", ".iso",
    },
    "Installers": {
        ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm",
        ".appimage", ".snap", ".apk", ".jar",
    },
    "Code": {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss",
        ".json", ".xml", ".yml", ".yaml", ".toml", ".ini", ".cfg",
        ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd",
        ".c", ".cpp", ".h", ".hpp", ".java", ".kt", ".go", ".rs",
        ".rb", ".php", ".sql", ".ipynb", ".r", ".lua", ".swift",
    },
}

FALLBACK_CATEGORY = "Other"


def get_category(extension: str, custom: dict | None = None) -> str:
    """Return the category name for an extension (dot included).

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
