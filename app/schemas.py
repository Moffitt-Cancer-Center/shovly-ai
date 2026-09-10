from pydantic import BaseModel, Field
from typing import Optional, List

class OnPremClusterCreate(BaseModel):
    name: str = Field(..., example="H100-DGX-Cluster-A")
    capex: float = Field(..., gt=0)
    lifecycle: float = Field(..., ge=1, le=50)
    opex: float = Field(..., ge=0)
    opex_period: str = Field("Annual", pattern="^(Annual|Monthly)$")
    funding_source: str = Field(...)
    note: Optional[str] = ""

class JobCostRequest(BaseModel):
    input_tokens: int = Field(1000, ge=1)
    output_tokens: int = Field(500, ge=1)
    tool_calls: int = Field(2, ge=0)
    tool_cost_per_call: float = Field(0.005, ge=0.0)
    retry_rate: float = Field(0.05, ge=0.0, lt=1.0)
    human_review_rate: float = Field(0.02, ge=0.0, le=1.0)
    human_review_cost: float = Field(0.50, ge=0.0)
    prompt_price_per_m: float = Field(..., ge=0.0)
    output_price_per_m: float = Field(..., ge=0.0)

class RFPScoringRequest(BaseModel):
    monthly_requests: int = 1_000_000
    avg_input_tokens: int = 1200
    avg_output_tokens: int = 400
    require_hipaa: bool = False
    require_zero_retention: bool = False
    require_soc2: bool = True
    min_sla: float = 99.9