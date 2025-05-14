from rich import get_console

from ._settings import get_settings

console = get_console()
settings = get_settings()
__all__ = ["console", "settings"]
