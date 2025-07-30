# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "SummarizeMemoryCreateParams",
    "SmartMemoryLocation",
    "SmartMemoryLocationSmartMemory",
    "SmartMemoryLocationSmartMemorySmartMemory",
]


class SummarizeMemoryCreateParams(TypedDict, total=False):
    memory_ids: Required[Annotated[List[str], PropertyInfo(alias="memoryIds")]]
    """List of memory IDs to summarize"""

    session_id: Required[Annotated[str, PropertyInfo(alias="sessionId")]]
    """Unique session identifier for the working memory instance"""

    smart_memory_location: Required[Annotated[SmartMemoryLocation, PropertyInfo(alias="smartMemoryLocation")]]
    """Smart memory locator for targeting the correct smart memory instance"""

    system_prompt: Annotated[Optional[str], PropertyInfo(alias="systemPrompt")]
    """Optional custom system prompt for summarization"""


class SmartMemoryLocationSmartMemorySmartMemory(TypedDict, total=False):
    name: Required[str]
    """The name of the smart memory **EXAMPLE** "my-smartmemory" **REQUIRED** TRUE"""

    application_name: Annotated[Optional[str], PropertyInfo(alias="applicationName")]
    """Optional Application **EXAMPLE** "my-app" **REQUIRED** FALSE"""

    version: Optional[str]
    """
    Optional version of the smart memory **EXAMPLE** "01jtryx2f2f61ryk06vd8mr91p"
    **REQUIRED** FALSE
    """


class SmartMemoryLocationSmartMemory(TypedDict, total=False):
    smart_memory: Required[Annotated[SmartMemoryLocationSmartMemorySmartMemory, PropertyInfo(alias="smartMemory")]]
    """
    **EXAMPLE** {"name":"memory-name","application_name":"demo","version":"1234"}
    **REQUIRED** TRUE
    """


SmartMemoryLocation: TypeAlias = Union[SmartMemoryLocationSmartMemory, object]
