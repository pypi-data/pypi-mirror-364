# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "RehydrateSessionRehydrateParams",
    "SmartMemoryLocation",
    "SmartMemoryLocationSmartMemory",
    "SmartMemoryLocationSmartMemorySmartMemory",
]


class RehydrateSessionRehydrateParams(TypedDict, total=False):
    session_id: Required[Annotated[str, PropertyInfo(alias="sessionId")]]
    """Session identifier to restore from episodic memory"""

    smart_memory_location: Required[Annotated[SmartMemoryLocation, PropertyInfo(alias="smartMemoryLocation")]]
    """Smart memory locator for targeting the correct smart memory instance"""

    summary_only: Annotated[Optional[bool], PropertyInfo(alias="summaryOnly")]
    """If true, only restore a summary. If false, restore all memories"""


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
