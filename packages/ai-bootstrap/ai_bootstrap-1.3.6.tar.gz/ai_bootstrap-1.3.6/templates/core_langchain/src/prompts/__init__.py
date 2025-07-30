"""Prompt modules for {{ project_name }}."""

from .templates import (
    get_basic_prompt,
    get_qa_prompt,
    get_custom_prompt,
    create_prompt_template,
    PROMPT_TEMPLATES,
)

__all__ = [
    "get_basic_prompt",
    "get_qa_prompt",
    "get_custom_prompt",
    "create_prompt_template",
    "PROMPT_TEMPLATES",
]
