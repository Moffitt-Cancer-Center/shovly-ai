from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from datetime import datetime
from app.database import Base

class OnPremCluster(Base):
    __tablename__ = "on_prem_clusters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    capex = Column(Float, nullable=False)
    lifecycle = Column(Float, nullable=False)  # In years
    opex = Column(Float, nullable=False)
    opex_period = Column(String(20), nullable=False, default="Annual")
    funding_source = Column(String(50), nullable=False)
    note = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class ProviderOffering(Base):
    __tablename__ = "provider_offerings"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(100), index=True)  # e.g., Fireworks AI, Together AI
    tier_category = Column(String(100), index=True)  # e.g., Specialized serverless inference clouds
    model_name = Column(String(100))
    prompt_price_per_m = Column(Float)   # $ per 1M input tokens
    output_price_per_m = Column(Float)   # $ per 1M output tokens
    rpm_limit = Column(Integer)
    tpm_limit = Column(Integer)
    ttft_ms = Column(Float)              # Time to first token
    tps = Column(Float)                  # Tokens per second
    sla_percentage = Column(Float)
    zero_data_retention = Column(Boolean, default=False)
    hipaa_compliant = Column(Boolean, default=False)
    soc2_compliant = Column(Boolean, default=False)
    eu_data_residency = Column(Boolean, default=False)