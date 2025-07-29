# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from ..._models import BaseModel

__all__ = ["FlashcardGetTypesResponse"]


class FlashcardGetTypesResponse(BaseModel):
    descriptions: Optional[Dict[str, str]] = None

    types: Optional[List[str]] = None
    """List of flashcard types"""
