"""
Teams Bot Utils - A comprehensive library for Microsoft Teams bot development

This package provides utilities for:
- Message content analysis and processing
- Image handling and encoding from Teams attachments
- Telemetry tracking with Mixpanel integration
- HTTP client management with connection pooling
- Activity extensions for Bot Framework
"""

__version__ = "1.0.1"
__author__ = "Shubham Shinde"
__email__ = "shubhamshinde7995@gmail.com"
__license__ = "MIT"

# Main exports
from activity.extensions import extend_activity_class, check_message_contents

# Image processing exports
try:
    from image.processing import (
        download_and_encode_image,
        process_image_attachment,
        extract_image_from_activity,
    )
except ImportError:
    # Handle case where images module might not be available
    pass

# Telemetry exports
try:
    from .telemetry.mixpanel_telemetry import BotTelemetry
except ImportError:
    # Handle case where telemetry module might not be available
    pass

# HTTP utilities exports
try:
    from .utils.http_client import HttpClient
    from .utils.connection_pool import get_http_client, close_all_clients
except ImportError:
    # Handle case where utils module might not be available
    pass

__all__ = [
    # Core functionality
    "extend_activity_class",
    "check_message_contents",
    # Image processing
    "download_and_encode_image",
    "process_image_attachment",
    "extract_image_from_activity",
    # Telemetry
    "BotTelemetry",
    # HTTP utilities
    "HttpClient",
    "get_http_client",
    "close_all_clients",
]
