from pydantic import BaseModel, Field
from typing import List


class UseCases(BaseModel):
    """A schema for generating a list of use cases."""

    use_cases: List[str] = Field(
        description="A diverse list of sample inputs (use cases) appropriate for the described prompt."
    )


class EvaluationResult(BaseModel):
    """A schema for the structured output of the Evaluator model."""

    pros: List[str] = Field(
        description="A list of strengths and things the response did well."
    )
    cons: List[str] = Field(
        description="A list of weaknesses, inaccuracies, or areas for improvement in the response."
    )
    quality_score: float = Field(
        description="A numerical score from 1.0 to 10.0 representing the overall quality of the response, where 10 is perfect.",
        ge=1.0,
        le=10.0,
    )
