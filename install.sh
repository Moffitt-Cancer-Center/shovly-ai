#!/usr/bin/env bash
set -eo pipefail

echo "=========================================================="
echo "          Shovly-ai Production Deployment Engine          "
echo "=========================================================="

# Check root or sudo privileges if needed
ROOT_CMD=""
if [ "$EUID" -ne 0 ]; then
    if command -v sudo >/dev/null 2>&1; then
        ROOT_CMD="sudo"
    else
        echo "[-] WARNING: Running as non-root without sudo. Some installation steps may fail."
    fi
fi

# 1. Dependency Validation
echo "[*] Step 1/4: Checking system dependencies..."
MISSING_DEPS=()
for tool in curl docker; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        MISSING_DEPS+=("$tool")
    fi
done

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "[-] Missing mandatory dependencies: ${MISSING_DEPS[*]}"
    echo "[*] Attempting to install missing packages..."
    if command -v apt-get >/dev/null 2>&1; then
        $ROOT_CMD apt-get update && $ROOT_CMD apt-get install -y "${MISSING_DEPS[@]}"
    elif command -v yum >/dev/null 2>&1; then
        $ROOT_CMD yum install -y "${MISSING_DEPS[@]}"
    else
        echo "[-] Automatic package manager detection failed. Please install ${MISSING_DEPS[*]} manually."
        exit 1
    fi
fi

# 2. Check Docker Daemon & Compose Support
echo "[*] Step 2/4: Verifying Docker runtime..."
if ! docker info >/dev/null 2>&1; then
    echo "[-] Docker is installed but the daemon is not running. Attempting to start..."
    $ROOT_CMD systemctl start docker || { echo "[-] Failed to start docker daemon."; exit 1; }
fi

COMPOSE_CMD=""
if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
else
    echo "[-] Docker Compose plugin not found. Installing compose plugin..."
    $ROOT_CMD apt-get update && $ROOT_CMD apt-get install -y docker-compose-plugin || {
        echo "[-] Failed to install Docker Compose automatically. Please install docker-compose-plugin."
        exit 1
    }
    COMPOSE_CMD="docker compose"
fi

# 3. Directory Layout and Storage Initialization
echo "[*] Step 3/4: Provisioning persistent volumes and file trees..."
mkdir -p data app/templates

# 4. Container Build & Orchestration
echo "[*] Step 4/4: Building and launching Shovly-ai container stack..."
$COMPOSE_CMD down --remove-orphans || true
$COMPOSE_CMD build --pull
$COMPOSE_CMD up -d

echo "[*] Waiting for container health probe..."
HEALTH_CHECK_ATTEMPTS=0
MAX_ATTEMPTS=20
until curl -s http://localhost:8000/healthz | grep -q '"status":"healthy"'; do
    HEALTH_CHECK_ATTEMPTS=$((HEALTH_CHECK_ATTEMPTS+1))
    if [ "$HEALTH_CHECK_ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
        echo "[-] Container failed to report healthy within 60 seconds."
        $COMPOSE_CMD logs
        exit 1
    fi
    sleep 3
done

echo ""
echo "=========================================================="
echo "    Shovly-ai Deployed Successfully (Production Ready)    "
echo "=========================================================="
echo "  URL:             http://localhost:8000"
echo "  Health Probe:    http://localhost:8000/healthz"
echo "  Data Volume:     shovly_sqlite_data (Persistent)"
echo "  Stop Platform:   $COMPOSE_CMD down"
echo "  Inspect Logs:    $COMPOSE_CMD logs -f"
echo "=========================================================="