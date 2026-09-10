# Shovly-ai

**Shovly-ai** is a production-grade inference provider decision framework, agentic job-cost modeling engine, and on-premises infrastructure total cost of ownership (TCO) calculator. Containerized via Docker and powered by FastAPI and SQLite, it ingests provider metrics across proprietary, serverless, hyperscaler, and private cluster archetypes to enable data-driven procurement and architecture governance.

---

## Key Capabilities

* **20-Provider Market Matrix:** Inspect and filter offerings across models, pricing per 1M tokens, concurrency limits (RPM/TPM), first-token latency (TTFT), sustained throughput, SLA guarantees, and enterprise compliance (SOC2 Type II, HIPAA, Zero Data Retention, EU Residency).
* **Deterministic Job-Cost Simulator:** Factors raw prompt/completion tokens, external function/tool invocations, non-deterministic failure and retry rates ($R$), and human-in-the-loop audit costs into a single unit-cost metric per successful job:
  $$\text{Cost}_{\text{job}} = \frac{\text{PromptCost} + \text{OutputCost} + \text{ToolCost}}{1 - R} + \text{ReviewCost}$$
* **Enterprise RFP Procurement Scorecard:** Automatically processes capacity, token budgets, and compliance constraints to output ranked vendor evaluations with audit disqualification logs.
* **On-Premises Infrastructure Amortization Engine:** Benchmarks hardware investments against commercial cloud pricing:
  * **Annual Total:** $(\text{CapEx} \div \text{lifecycle}) + \text{annualized OpEx}$
  * **Cost/hr:** $\text{Annual Total} \div 8,760$
  * **Historical Hybrid Benchmarking:** Prorates CapEx/OpEx over an evaluation window to plot a third benchmark line on the daily trend chart and derive **On-Prem Effective $/hr** ($\text{Prorated Cost} \div \text{Actual Compute Hours}$).
* **Persistent SQLite Storage:** Hardware configurations survive restarts via persistent Docker volumes.

---

## Supported Inference Archetypes & Providers

Shovly-ai ingests specifications from the following core categories:

1. **First-Party Proprietary APIs:** OpenAI Direct, Anthropic Direct, Google Cloud Vertex
2. **Premium Shared-Capacity Tiers:** Fireworks AI, Together AI
3. **Hyperscaler Managed Model Services:** AWS Bedrock, Azure AI Studio, OCI GenAI
4. **Specialized Serverless Inference Clouds:** SiliconFlow, Inference.net, ComputePrices API, Kingly AI, DeepInfra
5. **Routing & Aggregation Layers:** OpenRouter, Portkey Gateway, Martian Router
6. **Dedicated or Self-Hosted Infrastructure:** CoreWeave Cloud, Lambda Labs, Nebius AI Studio

---

## Installation & Deployment

### Method 1: Automated Script (Recommended)

Clone the repository and run the setup script:

```bash
git clone https://github.com/Moffitt-Cancer-Center/shovly-ai.git
cd shovly-ai
chmod +x install.sh
./install.sh
```

The script verifies prerequisites (curl, docker, docker compose), provisions storage, builds the container image, and validates the `/healthz` probe.

### Method 2: Manual Docker Compose

```bash
# Clone and enter directory
git clone https://github.com/Moffitt-Cancer-Center/shovly-ai.git
cd shovly-ai

# Build and start services in detached mode
docker compose up -d --build

# Verify container health
curl -s http://localhost:8000/healthz
```

Access the dashboard at `http://localhost:8000`.

### Method 3: Native Host Execution (Development)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the app locally with hot reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Usage Guide

### 1. Market Matrix & Decision Framework

* Navigate to the Market Matrix section of the dashboard.
* Filter the table using the Architectural Categories dropdown (e.g., Specialized serverless inference clouds).
* Compare rates per million tokens against time-to-first-token (TTFT) and compliance tags (ZDR, HIPAA, SOC2).

### 2. Job-Cost Modeling

Enter your workload's token parameters in the Job Cost Calculator panel:

* **Input/Output Tokens:** Mean prompt and generation sizes.
* **Input/Output $/1M Tokens:** Selected provider rates.
* **Tool Calls per Job:** Number of external function invocations per execution.
* **Retry Rate ($R$):** Expected rate of retries due to parsing errors, timeouts, or hallucination guards ($0 \le R < 1$).
* **Human Review Rate:** Percentage of edge-case runs escalated to a human evaluator.

Click **Compute Unit Cost** to inspect the total cost per successful run.

### 3. Enterprise RFP Procurement Evaluation

* Go to the Enterprise RFP Evaluation Engine section.
* Set your Monthly Request Volume and Minimum SLA Target.
* Toggle mandatory compliance constraints: Mandate HIPAA, Mandate Zero Data Retention, or Mandate SOC2 Type II.
* Click **Generate RFP Evidence** to generate a ranked evaluation table with vendor disqualification audits.

### 4. On-Premises Cost Calculator & Daily Chart Benchmarking

* Open the On-Premises Infrastructure Cluster Calculator collapsible drawer at the bottom of the page.
* Add your cluster specifications:
  * **Cluster Identifier:** e.g., `DGX-H100-Node-01`
  * **CapEx ($):** Total hardware acquisition and installation cost.
  * **Lifecycle (yrs):** Depreciation schedule (1 to 50 years).
  * **OpEx ($):** Power, cooling, colocation, and maintenance costs.
  * **OpEx Period:** Annual or Monthly.
  * **Funding Source:** Select Federal Grant, Philanthropy, Capital Fund, Departmental, or Other.
  * **Attribution Note:** Free-text accounting/grant identifier.
* Click **Commit Cluster to SQLite**.

The calculator derives the Annual Total and Cost/hr ($\text{Annual Total} \div 8760$), and updates the green line on the Hybrid Cost Benchmark Chart to show prorated CapEx/OpEx alongside cloud pricing. Use **Clear** to remove an entry and rebalance the historical baseline.

---

## API Reference

### Health Probe

**Endpoint:** `GET /healthz`

**Response:**

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-09-10T18:14:00.000000"
}
```

### Add On-Prem Cluster

**Endpoint:** `POST /api/clusters`

**Payload:** `multipart/form-data`

| Field | Type | Notes |
| --- | --- | --- |
| `name` | string | Cluster identifier |
| `capex` | float | Must be greater than 0 |
| `lifecycle` | float | 1–50 years |
| `opex` | float | Must be 0 or greater |
| `opex_period` | string | `"Annual"` or `"Monthly"` |
| `funding_source` | string | Accounting/grant category |
| `note` | string | Optional attribution note |

### Clear On-Prem Cluster

**Endpoint:** `DELETE /api/clusters/{cluster_id}`

**Response:**

```json
{
  "status": "success",
  "deleted_cluster_id": 1
}
```

### Compute Job Unit Cost

**Endpoint:** `POST /api/calculate-job-cost`

**Headers:** `Content-Type: application/json`

**Payload:**

```json
{
  "input_tokens": 1500,
  "output_tokens": 500,
  "prompt_price_per_m": 0.90,
  "output_price_per_m": 0.90,
  "tool_calls": 3,
  "tool_cost_per_call": 0.002,
  "retry_rate": 0.08,
  "human_review_rate": 0.01,
  "human_review_cost": 0.50
}
```

### Generate RFP Scorecard

**Endpoint:** `POST /api/rfp-scorecard`

**Headers:** `Content-Type: application/json`

**Payload:**

```json
{
  "monthly_requests": 2500000,
  "avg_input_tokens": 1200,
  "avg_output_tokens": 400,
  "require_hipaa": true,
  "require_zero_retention": true,
  "require_soc2": true,
  "min_sla": 99.9
}
```

---

## Production Service Management

Two systemd unit templates are provided for running Shovly-ai on a Linux host:

* **`shovly-ai.service`** — Runs the Dockerized stack via `docker compose`. Install to `/opt/shovly-ai`, then:

  ```bash
  sudo cp shovly-ai.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable --now shovly-ai.service
  ```

* **`shovly-ai-native.service`** — Runs Uvicorn directly from a Python virtual environment (no Docker). Requires a dedicated `shovly` system user, a virtual environment at `/opt/shovly-ai/venv`, and dependencies installed via `pip install -r requirements.txt`:

  ```bash
  sudo cp shovly-ai-native.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable --now shovly-ai-native.service
  ```

Use only one of the two service definitions per host, depending on whether you are deploying via Docker or as a native process.

## License

MIT License — see [LICENSE](LICENSE) for details.
