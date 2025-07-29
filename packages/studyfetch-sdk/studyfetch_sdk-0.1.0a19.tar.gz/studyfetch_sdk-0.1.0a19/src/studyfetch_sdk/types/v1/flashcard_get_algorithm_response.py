# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from ..._models import BaseModel

__all__ = ["FlashcardGetAlgorithmResponse", "Intervals", "Ratings"]


class Intervals(BaseModel):
    graduated: Optional[str] = None
    """Description of graduated intervals"""

    lapse: Optional[str] = None
    """Description of lapse intervals"""

    learning: Optional[List[float]] = None
    """Learning intervals in minutes"""


class Ratings(BaseModel):
    description: str
    """Rating description"""

    name: str
    """Rating name"""


class FlashcardGetAlgorithmResponse(BaseModel):
    algorithm: Optional[str] = None
    """Algorithm name"""

    intervals: Optional[Intervals] = None

    phases: Optional[Dict[str, str]] = None

    ratings: Optional[Dict[str, Ratings]] = None
