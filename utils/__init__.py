"""Utility functions package."""

from .validators import DataValidator
from .helpers import format_file_size, format_number, create_download_link
from .taiwan_weather_helper import TaiwanWeatherProcessor

__all__ = ['DataValidator', 'format_file_size', 'format_number', 'create_download_link', 'TaiwanWeatherProcessor']
def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis."""
    if not isinstance(text, str):
        text = str(text)
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."
