"""
Utility functions for Demiurg agents.
"""

from .files import (
    download_file,
    get_file_info,
    encode_file_base64,
    is_file_message,
    get_file_type,
    create_file_content,
)
from .tools import (
    init_tools,
    execute_tools,
    format_tool_results,
    get_tool_provider,
    register_tool_provider,
    ToolProvider,
)
from .audio import (
    get_audio_format,
    is_format_supported,
    convert_audio_to_wav,
    ensure_supported_format,
    check_ffmpeg_available,
)

__all__ = [
    # File utilities
    "download_file",
    "get_file_info",
    "encode_file_base64",
    "is_file_message",
    "get_file_type",
    "create_file_content",
    # Tool utilities
    "init_tools",
    "execute_tools",
    "format_tool_results",
    "get_tool_provider",
    "register_tool_provider",
    "ToolProvider",
    # Audio utilities
    "get_audio_format",
    "is_format_supported",
    "convert_audio_to_wav",
    "ensure_supported_format",
    "check_ffmpeg_available",
]