from pydantic import BaseModel, Field
from typing import List, Literal


class RCAResponse(BaseModel):
    root_cause: str = Field(..., min_length=5)
    severity: Literal["low", "medium", "high", "critical"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    recommended_actions: List[str] = Field(..., min_length=1)