# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["AssignmentGraderCreateParams", "Rubric", "RubricCriterion"]


class AssignmentGraderCreateParams(TypedDict, total=False):
    rubric: Required[Rubric]
    """Grading rubric"""

    title: Required[str]
    """Title of the assignment"""

    material_id: Annotated[str, PropertyInfo(alias="materialId")]
    """Material ID to grade"""

    model: str
    """AI model to use"""

    text_to_grade: Annotated[str, PropertyInfo(alias="textToGrade")]
    """Text content to grade"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID for tracking"""


class RubricCriterion(TypedDict, total=False):
    points_possible: Required[Annotated[float, PropertyInfo(alias="pointsPossible")]]
    """Points possible for this criterion"""

    title: Required[str]
    """Title of the criterion"""

    description: str
    """Description of the criterion"""


class Rubric(TypedDict, total=False):
    criteria: Required[Iterable[RubricCriterion]]
    """Grading criteria"""
