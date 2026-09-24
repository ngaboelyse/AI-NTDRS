from typing import Literal

from pydantic import BaseModel, Field


class CopilotMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=1500)


class CopilotQueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    history: list[CopilotMessage] = Field(default_factory=list, max_length=8)


class CopilotSummary(BaseModel):
    answer: str
    assistant_mode: str = "fallback"
    model_name: str = "Rule-based assistant"
    show_context: bool = True
    facts: list[str]
    predictions: list[str]
    recommendations: list[str]
    unknowns: list[str]
    related_devices: list[dict]
    related_alerts: list[dict]
