# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["FlashcardBatchProcessResponse", "Result"]


class Result(BaseModel):
    card_id: str = FieldInfo(alias="cardId")
    """Flashcard ID"""

    success: bool
    """Operation success"""

    error: Optional[str] = None
    """Error message if failed"""

    result: Optional[object] = None
    """Operation result"""


class FlashcardBatchProcessResponse(BaseModel):
    failed: Optional[float] = None
    """Failed operations"""

    processed: Optional[float] = None
    """Total operations processed"""

    results: Optional[List[Result]] = None

    success: Optional[bool] = None
    """Overall success"""

    successful: Optional[float] = None
    """Successful operations"""
