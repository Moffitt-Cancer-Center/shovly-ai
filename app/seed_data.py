from sqlalchemy.orm import Session
from app.models import ProviderOffering

SAMPLE_OFFERINGS = [
    # First-party proprietary model APIs
    {"provider_name": "OpenAI Direct", "tier_category": "First-party proprietary model APIs", "model_name": "GPT-4o", "prompt_price_per_m": 5.00, "output_price_per_m": 15.00, "rpm_limit": 10000, "tpm_limit": 2000000, "ttft_ms": 320, "tps": 110, "sla_percentage": 99.9, "zero_data_retention": True, "hipaa_compliant": True, "soc2_compliant": True, "eu_data_residency": True},
    {"provider_name": "Anthropic Direct", "tier_category": "First-party proprietary model APIs", "model_name": "Claude 3.5 Sonnet", "prompt_price_per_m": 3.00, "output_price_per_m": 15.00, "rpm_limit": 8000, "tpm_limit": 1600000, "ttft_ms": 340, "tps": 85, "sla_percentage": 99.9, "zero_data_retention": True, "hipaa_compliant": True, "soc2_compliant": True, "eu_data_residency": False},
    {"provider_name": "Google Cloud Vertex", "tier_category": "First-party proprietary model APIs", "model_name": "Gemini 1.5 Pro", "prompt_price_per_m": 3.50, "output_price_per_m": 10.50, "rpm_limit": 12000, "tpm_limit": 4000000, "ttft_ms": 290, "tps": 95, "sla_percentage": 99.95, "zero_data_retention": True, "hipaa_compliant": True, "soc2_compliant": True, "eu_data_residency": True},

    # Premium shared-capacity tiers
    {"provider_name": "Fireworks AI", "tier_category": "Premium shared-capacity tiers", "model_name": "Llama-3.3-70B-Instruct", "prompt_price_per_m": 0.90, "output_price_per_m": 0.90, "rpm_limit": 20000, "tpm_limit": 5000000, "ttft_ms": 140, "tps": 145, "sla_percentage": 99.9, "zero_data_retention": True, "hipaa_compliant": True, "soc2_compliant": True, "eu_data_residency": False},
    {"provider_name": "Together AI", "tier_category": "Premium shared-capacity tiers", "model_name": "Llama-3.3-70B-Turbo", "prompt_price_per_m": 0.88, "output_price_per_m": 0.88, "rpm_limit": 18000, "tpm_limit": 4500000, "ttft_ms": 150, "tps": 135, "sla_percentage": 99.9, "zero_data_retention": False, "hipaa_compliant": False, "soc2_compliant": True, "eu_data_residency": False},
    {"provider_name": "Together AI", "tier_category": "Premium shared-capacity tiers", "model_name": "DeepSeek-V3", "prompt_price_per_m": 1.25, "output_price_per_m": 1.25, "rpm_limit": 10000, "tpm_limit": 3000000, "ttft_ms": 220, "tps": 80, "sla_percentage": 99.9, "zero_data_retention": False, "hipaa_compliant": False, "soc2_compliant": True, "eu_data_residency": False},

    # Hyperscaler managed model services
    {"provider_name": "AWS Bedrock", "tier_category": "Hyperscaler managed model services", "model_name": "Claude 3.5 Haiku", "prompt_price_per_m": 0.80, "output_price_per_m": 4.00, "rpm_limit": 25000, "tpm_limit": 8000000, "ttft_ms": 210, "tps": 120, "sla_percentage": 99.99, "zero_data_retention": True, "hipaa_compliant": True, "soc2_compliant": True, "eu_data_residency": True},
    {"provider_name": "Azure AI Studio", "tier_category": "Hyperscaler managed model services", "model_name": "GPT-4o Mini", "prompt_price_per_m": 0.15, "output_price_per_m": 0.60, "rpm_limit": 30000, "tpm_limit": 10000000, "ttft_ms": 190, "tps": 150, "sla_percentage": 99.99, "zero_data_retention": True, "hipaa_compliant": True, "soc2_compliant": True, "eu_data_residency": True},
    {"provider_name": "OCI GenAI", "tier_category": "Hyperscaler managed model services", "model_name": "Command-R+", "prompt_price_per_m": 2.50, "output_price_per_m": 10.00, "rpm_limit": 10000, "tpm_limit": 2000000, "ttft_ms": 380, "tps": 65, "sla_percentage": 99.9, "zero_data_retention": True, "hipaa_compliant": True, "soc2_compliant": True, "eu_data_residency": True},

    # Specialized serverless inference clouds
    {"provider_name": "SiliconFlow", "tier_category": "Specialized serverless inference clouds", "model_name": "Qwen-2.5-72B-Instruct", "prompt_price_per_m": 0.55, "output_price_per_m": 0.55, "rpm_limit": 15000, "tpm_limit": 3000000, "ttft_ms": 180, "tps": 115, "sla_percentage": 99.8, "zero_data_retention": False, "hipaa_compliant": False, "soc2_compliant": False, "eu_data_residency": False},
    {"provider_name": "Inference.net", "tier_category": "Specialized serverless inference clouds", "model_name": "Llama-3.1-8B-Instant", "prompt_price_per_m": 0.10, "output_price_per_m": 0.10, "rpm_limit": 50000, "tpm_limit": 15000000, "ttft_ms": 90, "tps": 220, "sla_percentage": 99.9, "zero_data_retention": True, "hipaa_compliant": False, "soc2_compliant": True, "eu_data_residency": False},
    {"provider_name": "ComputePrices API", "tier_category": "Specialized serverless inference clouds", "model_name": "Mixtral-8x22B-v0.1", "prompt_price_per_m": 0.90, "output_price_per_m": 0.90, "rpm_limit": 12000, "tpm_limit": 2500000, "ttft_ms": 280, "tps": 85, "sla_percentage": 99.5, "zero_data_retention": False, "hipaa_compliant": False, "soc2_compliant": False, "eu_data_residency": False},
    {"provider_name": "Kingly AI", "tier_category": "Specialized serverless inference clouds", "model_name": "Llama-3.3-70B-Fast", "prompt_price_per_m": 0.75, "output_price_per_m": 0.75, "rpm_limit": 15000, "tpm_limit": 3500000, "ttft_ms": 130, "tps": 160, "sla_percentage": 99.9, "zero_data_retention": True, "hipaa_compliant": True, "soc2_compliant": True, "eu_data_residency": False},
    {"provider_name": "DeepInfra", "tier_category": "Specialized serverless inference clouds", "model_name": "Llama-3.1-405B-FP8", "prompt_price_per_m": 2.50, "output_price_per_m": 2.50, "rpm_limit": 5000, "tpm_limit": 1000000, "ttft_ms": 420, "tps": 45, "sla_percentage": 99.7, "zero_data_retention": False, "hipaa_compliant": False, "soc2_compliant": True, "eu_data_residency": False},

    # Routing and aggregation layers
    {"provider_name": "OpenRouter", "tier_category": "Routing and aggregation layers", "model_name": "Auto-Route Optimization", "prompt_price_per_m": 0.85, "output_price_per_m": 0.85, "rpm_limit": 40000, "tpm_limit": 8000000, "ttft_ms": 170, "tps": 130, "sla_percentage": 99.85, "zero_data_retention": False, "hipaa_compliant": False, "soc2_compliant": False, "eu_data_residency": False},
    {"provider_name": "Portkey Gateway", "tier_category": "Routing and aggregation layers", "model_name": "Failover-Virtual-Key", "prompt_price_per_m": 1.00, "output_price_per_m": 1.00, "rpm_limit": 100000, "tpm_limit": 20000000, "ttft_ms": 110, "tps": 180, "sla_percentage": 99.99, "zero_data_retention": True, "hipaa_compliant": True, "soc2_compliant": True, "eu_data_residency": True},
    {"provider_name": "Martian Router", "tier_category": "Routing and aggregation layers", "model_name": "Model-Intelligence-Router", "prompt_price_per_m": 0.95, "output_price_per_m": 1.20, "rpm_limit": 25000, "tpm_limit": 5000000, "ttft_ms": 200, "tps": 110, "sla_percentage": 99.9, "zero_data_retention": True, "hipaa_compliant": False, "soc2_compliant": True, "eu_data_residency": False},

    # Dedicated or self-hosted infrastructure
    {"provider_name": "CoreWeave Cloud", "tier_category": "Dedicated or self-hosted infrastructure", "model_name": "8x H100 SXM5 Reservation", "prompt_price_per_m": 0.35, "output_price_per_m": 0.35, "rpm_limit": 200000, "tpm_limit": 50000000, "ttft_ms": 65, "tps": 320, "sla_percentage": 99.99, "zero_data_retention": True, "hipaa_compliant": True, "soc2_compliant": True, "eu_data_residency": True},
    {"provider_name": "Lambda Labs On-Demand", "tier_category": "Dedicated or self-hosted infrastructure", "model_name": "8x A100 80GB Node", "prompt_price_per_m": 0.45, "output_price_per_m": 0.45, "rpm_limit": 150000, "tpm_limit": 35000000, "ttft_ms": 85, "tps": 240, "sla_percentage": 99.95, "zero_data_retention": True, "hipaa_compliant": True, "soc2_compliant": True, "eu_data_residency": False},
    {"provider_name": "Nebius AI Studio", "tier_category": "Dedicated or self-hosted infrastructure", "model_name": "H100 PCIe Dedicated Slice", "prompt_price_per_m": 0.40, "output_price_per_m": 0.40, "rpm_limit": 180000, "tpm_limit": 40000000, "ttft_ms": 70, "tps": 290, "sla_percentage": 99.99, "zero_data_retention": True, "hipaa_compliant": True, "soc2_compliant": True, "eu_data_residency": True},
]

def seed_providers(db: Session):
    if db.query(ProviderOffering).count() == 0:
        for item in SAMPLE_OFFERINGS:
            offering = ProviderOffering(**item)
            db.add(offering)
        db.commit()