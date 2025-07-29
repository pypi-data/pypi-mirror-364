# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["TestCreateParams"]


class TestCreateParams(TypedDict, total=False):
    component_id: Required[Annotated[str, PropertyInfo(alias="componentId")]]
    """Component ID"""

    name: str
    """Test name (optional)"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID (optional)"""
