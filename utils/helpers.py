"""Helper utility functions."""

import base64
import streamlit as st
from typing import Any, Optional

def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_number(num: float) -> str:
    """Format large numbers with commas."""
    if num is None or num != num:  # Check for NaN
        return "N/A"
    
    if isinstance(num, (int, float)):
        return f"{num:,.0f}" if num == int(num) else f"{num:,.2f}"
    
    return str(num)

def create_download_link(data: Any, filename: str, link_text: str = "Download") -> str:
    """Create a download link for data."""
    if isinstance(data, str):
        # Text data
        b64 = base64.b64encode(data.encode()).decode()
        mime_type = "text/plain"
    else:
        # Binary data
        b64 = base64.b64encode(data).decode()
        mime_type = "application/octet-stream"
    
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}" target="_blank">{link_text}</a>'
    return href

def safe_get(dictionary: dict, key: str, default: Any = None) -> Any:
    """Safely get a value from dictionary with nested key support."""
    try:
        keys = key.split('.')
        value = dictionary
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis."""
    if not isinstance(text, str):
        text = str(text)
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def validate_url(url: str) -> bool:
    """Validate if string is a valid URL."""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None