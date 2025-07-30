"""Processor modules for {{ project_name }}."""

from typing import List

modalities = globals().get("modalities", [])

if 'image' in modalities:
    from .image_processor import ImageProcessor
if 'audio' in modalities:
    from .audio_processor import AudioProcessor

__all__: List[str] = []
if 'image' in modalities:
    __all__.append("ImageProcessor")
if 'audio' in modalities:
    __all__.append("AudioProcessor")
