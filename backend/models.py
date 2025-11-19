from typing import List, Optional

from pydantic import BaseModel, Field


class DebateConfig(BaseModel):
    num_solutions: int = Field(4, ge=3, le=5, description="Number of candidate proposals")
    num_batches: int = Field(2, ge=1, le=5, description="Number of debate batches")
    rounds_per_batch: int = Field(2, ge=1, le=5, description="Rounds per batch")
    model: Optional[str] = Field(
        None, description="Override default OpenAI model, e.g. gpt-4.1"
    )


class DebateRequest(BaseModel):
    topic: str = Field(..., description="Debate topic / policy / thesis")
    config: DebateConfig = Field(default_factory=DebateConfig)
    language: str = Field("en", description="Output language code, default en")


class DebateTurn(BaseModel):
    batch: int
    round: int
    agent_name: str
    role: str
    content: str


class ProposalInfo(BaseModel):
    id: int
    name: str
    summary: str


class AgentInfo(BaseModel):
    name: str
    proposal_id: int
    role: str


class DebateResult(BaseModel):
    topic: str
    proposals: List[ProposalInfo]
    agents: List[AgentInfo]
    history: List[DebateTurn]
    final_report: str


class DebateResponse(BaseModel):
    result: DebateResult


