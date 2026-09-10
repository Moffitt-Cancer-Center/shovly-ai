from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import OnPremCluster, ProviderOffering
from app.schemas import JobCostRequest, RFPScoringRequest
from app.seed_data import seed_providers

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    seed_providers(db)
    yield

app = FastAPI(
    title="Shovly-ai Platform",
    description="LLM Inference Provider Decision Framework, Job-Cost Simulator, and On-Prem Benchmark Engine",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")

@app.get("/healthz")
async def healthz(db: Session = Depends(get_db)):
    try:
        db.execute(Base.metadata.tables["on_prem_clusters"].select().limit(1))
        return {"status": "healthy", "database": "connected", "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database check failed: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(
    request: Request,
    tier_filter: Optional[str] = None,
    eval_days: int = 30,
    compute_hours: float = 500.0,
    db: Session = Depends(get_db)
):
    query = db.query(ProviderOffering)
    if tier_filter and tier_filter != "All":
        query = query.filter(ProviderOffering.tier_category == tier_filter)
    offerings = query.all()

    clusters = db.query(OnPremCluster).all()
    cluster_view = []
    
    total_annualized_on_prem = 0.0
    for c in clusters:
        ann_opex = c.opex * 12.0 if c.opex_period.lower() == "monthly" else c.opex
        annual_total = (c.capex / c.lifecycle) + ann_opex
        cost_per_hr = annual_total / 8760.0
        total_annualized_on_prem += annual_total
        
        cluster_view.append({
            "id": c.id,
            "name": c.name,
            "capex": c.capex,
            "lifecycle": c.lifecycle,
            "opex": c.opex,
            "opex_period": c.opex_period,
            "funding_source": c.funding_source,
            "note": c.note,
            "annual_total": annual_total,
            "cost_per_hr": cost_per_hr
        })

    # Historical On-Premise Metrics for selected window
    days = max(eval_days, 1)
    hrs = max(compute_hours, 1.0)
    prorated_on_prem_total = total_annualized_on_prem * (days / 365.0)
    on_prem_eff_hourly = prorated_on_prem_total / hrs

    distinct_tiers = [
        "First-party proprietary model APIs",
        "Premium shared-capacity tiers",
        "Hyperscaler managed model services",
        "Specialized serverless inference clouds",
        "Routing and aggregation layers",
        "Dedicated or self-hosted infrastructure"
    ]

    return templates.TemplateResponse(request, "index.html", {
        "offerings": offerings,
        "clusters": cluster_view,
        "tiers": distinct_tiers,
        "selected_tier": tier_filter or "All",
        "eval_days": days,
        "compute_hours": hrs,
        "prorated_on_prem_total": prorated_on_prem_total,
        "on_prem_eff_hourly": on_prem_eff_hourly,
        "total_annualized_on_prem": total_annualized_on_prem
    })

@app.post("/api/clusters")
async def create_cluster(
    name: str = Form(...),
    capex: float = Form(..., gt=0),
    lifecycle: float = Form(..., ge=1, le=50),
    opex: float = Form(..., ge=0),
    opex_period: str = Form("Annual", pattern="^(Annual|Monthly)$"),
    funding_source: str = Form(...),
    note: str = Form(""),
    db: Session = Depends(get_db)
):
    cluster = OnPremCluster(
        name=name.strip(),
        capex=capex,
        lifecycle=lifecycle,
        opex=opex,
        opex_period=opex_period,
        funding_source=funding_source,
        note=note.strip()
    )
    db.add(cluster)
    db.commit()
    db.refresh(cluster)
    return JSONResponse(status_code=201, content={"status": "success", "cluster_id": cluster.id})

@app.delete("/api/clusters/{cluster_id}")
async def delete_cluster(cluster_id: int, db: Session = Depends(get_db)):
    cluster = db.query(OnPremCluster).filter(OnPremCluster.id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    db.delete(cluster)
    db.commit()
    return {"status": "success", "deleted_cluster_id": cluster_id}

@app.post("/api/calculate-job-cost")
async def calculate_job_cost(payload: JobCostRequest):
    """
    Cost per job calculation:
    Raw Request Cost = (prompt_tokens * prompt_price_per_m / 1M) + (output_tokens * output_price_per_m / 1M) + (tool_calls * tool_cost_per_call)
    Factoring Retry Rate (R): Expected attempts per successful job = 1 / (1 - R)
    Cost per Successful Job = (Raw Request Cost / (1 - R)) + (human_review_rate * human_review_cost)
    """
    token_cost = (
        (payload.input_tokens * (payload.prompt_price_per_m / 1_000_000.0)) +
        (payload.output_tokens * (payload.output_price_per_m / 1_000_000.0))
    )
    tool_cost = payload.tool_calls * payload.tool_cost_per_call
    single_attempt_cost = token_cost + tool_cost
    
    # Mathematical geometric series adjustment for retries
    expected_inference_cost = single_attempt_cost / (1.0 - payload.retry_rate)
    human_overhead = payload.human_review_rate * payload.human_review_cost
    total_cost_per_successful_job = expected_inference_cost + human_overhead

    return {
        "single_attempt_cost": round(single_attempt_cost, 6),
        "expected_attempts": round(1.0 / (1.0 - payload.retry_rate), 2),
        "inference_retry_cost": round(expected_inference_cost, 6),
        "human_overhead": round(human_overhead, 6),
        "total_cost_per_successful_job": round(total_cost_per_successful_job, 6)
    }

@app.post("/api/rfp-scorecard")
async def generate_rfp_scorecard(req: RFPScoringRequest, db: Session = Depends(get_db)):
    offerings = db.query(ProviderOffering).all()
    scorecard = []

    for item in offerings:
        rejection_reasons = []
        if req.require_hipaa and not item.hipaa_compliant:
            rejection_reasons.append("Missing HIPAA compliance")
        if req.require_zero_retention and not item.zero_data_retention:
            rejection_reasons.append("Missing Zero Data Retention guarantee")
        if req.require_soc2 and not item.soc2_compliant:
            rejection_reasons.append("Missing SOC2 certification")
        if item.sla_percentage < req.min_sla:
            rejection_reasons.append(f"SLA {item.sla_percentage}% below threshold {req.min_sla}%")

        # Projected Monthly Cost
        monthly_input_m = (req.monthly_requests * req.avg_input_tokens) / 1_000_000.0
        monthly_output_m = (req.monthly_requests * req.avg_output_tokens) / 1_000_000.0
        projected_monthly_cost = (monthly_input_m * item.prompt_price_per_m) + (monthly_output_m * item.output_price_per_m)

        # Composite score (100 base)
        score = 100.0
        if rejection_reasons:
            score -= (len(rejection_reasons) * 30.0)
        
        # Penalize higher latency & reward high throughput
        score -= min(item.ttft_ms / 10.0, 25.0)
        score += min(item.tps / 10.0, 20.0)

        scorecard.append({
            "provider": item.provider_name,
            "model": item.model_name,
            "tier": item.tier_category,
            "projected_monthly_cost": round(projected_monthly_cost, 2),
            "compliant": len(rejection_reasons) == 0,
            "disqualifications": rejection_reasons,
            "composite_procurement_score": round(max(score, 0.0), 1)
        })

    scorecard.sort(key=lambda x: (not x["compliant"], -x["composite_procurement_score"], x["projected_monthly_cost"]))
    return scorecard