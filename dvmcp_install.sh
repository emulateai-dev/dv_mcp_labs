#!/bin/bash

# ============================================================
#  DVMCP - Damn Vulnerable MCP Server - Install Script
#  Supports: Ubuntu / Debian-based Linux
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info()    { echo -e "${GREEN}[+]${NC} $1"; }
warn()    { echo -e "${YELLOW}[!]${NC} $1"; }
error()   { echo -e "${RED}[✗]${NC} $1"; exit 1; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }

echo ""
echo "=============================================="
echo "   Damn Vulnerable MCP Server - Installer"
echo "=============================================="
echo ""

# ── 1. Check OS ──────────────────────────────────
info "Checking OS..."
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    warn "This script is designed for Linux. Detected: $OSTYPE"
    read -p "Continue anyway? (y/N): " cont
    [[ "$cont" =~ ^[Yy]$ ]] || exit 1
fi

# ── 2. Install Python 3.10+ ──────────────────────
info "Checking Python 3.10+..."
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c 'import sys; print(sys.version_info.minor)')
    PY_MAJ=$(python3 -c 'import sys; print(sys.version_info.major)')
    if [[ "$PY_MAJ" -ge 3 && "$PY_VER" -ge 10 ]]; then
        success "Python $(python3 --version) found."
    else
        warn "Python version too old (need 3.10+). Installing..."
        sudo apt-get update -qq
        sudo apt-get install -y python3.10 python3.10-venv python3-pip
    fi
else
    info "Python3 not found. Installing..."
    sudo apt-get update -qq
    sudo apt-get install -y python3.10 python3.10-venv python3-pip
fi

# ── 3. Create virtual environment ────────────────
info "Setting up Python virtual environment..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    success "Virtual environment created."
else
    success "Virtual environment already exists."
fi

# ── 4. Install Python dependencies ───────────────
info "Installing Python dependencies..."
./venv/bin/pip install --quiet --upgrade pip
./venv/bin/pip install --quiet -r requirements.txt
success "Python dependencies installed."

# ── 5. Install Ollama ─────────────────────────────
info "Checking Ollama..."
if command -v ollama &>/dev/null; then
    success "Ollama already installed: $(ollama --version)"
else
    info "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    success "Ollama installed."
fi

# ── 6. Start Ollama service ───────────────────────
info "Starting Ollama service..."
if pgrep -x "ollama" > /dev/null; then
    success "Ollama is already running."
else
    ollama serve &>/dev/null &
    sleep 3
    success "Ollama service started."
fi

# ── 7. Download jailbroken Llama3 model ──────────
GGUF_FILENAME="Meta-Llama-3-8B-Instruct-Jailbroken.Q4_K_M.gguf"
GGUF_URL="https://huggingface.co/mradermacher/Meta-Llama-3-8B-Instruct-Jailbroken-GGUF/resolve/main/${GGUF_FILENAME}"
GGUF_PATH="$(pwd)/models/${GGUF_FILENAME}"
MODELFILE_PATH="$(pwd)/Modelfile"

mkdir -p "$(pwd)/models"

if [[ -f "$GGUF_PATH" ]]; then
    success "Model file already exists: $GGUF_PATH"
else
    info "Downloading jailbroken Llama3 model (~4.9GB) from HuggingFace..."
    info "Source: https://huggingface.co/mradermacher/Meta-Llama-3-8B-Instruct-Jailbroken-GGUF"
    wget --show-progress -q -O "$GGUF_PATH" "$GGUF_URL" \
        || curl -L --progress-bar -o "$GGUF_PATH" "$GGUF_URL" \
        || error "Failed to download model. Check your internet connection and try again."
    success "Model downloaded: $GGUF_PATH"
fi

# ── 8. Create Modelfile and register with Ollama ──
info "Registering model with Ollama..."
cat > "$MODELFILE_PATH" <<EOF
FROM ${GGUF_PATH}
EOF

ollama create jailbroken-llama -f "$MODELFILE_PATH"
success "Model 'jailbroken-llama' registered with Ollama."

# ── 9. Make shell scripts executable ─────────────
info "Setting permissions on shell scripts..."
chmod +x start_sse_servers.sh startup.sh
success "Permissions set."

# ── 9. Run setup for challenge environments ───────
info "Setting up challenge environments..."
mkdir -p /tmp/dvmcp_challenge3/public /tmp/dvmcp_challenge3/private
mkdir -p /tmp/dvmcp_challenge4/state
mkdir -p /tmp/dvmcp_challenge6/user_uploads
mkdir -p /tmp/dvmcp_challenge8/sensitive
mkdir -p /tmp/dvmcp_challenge10/config

echo '{"weather_tool_calls": 0}' > /tmp/dvmcp_challenge4/state/state.json
echo "Welcome to the public directory!" > /tmp/dvmcp_challenge3/public/welcome.txt
echo "This is a public file." > /tmp/dvmcp_challenge3/public/public_file.txt
success "Challenge environments ready."

# ── Done ──────────────────────────────────────────
echo ""
echo "=============================================="
echo -e "${GREEN}   Installation Complete!${NC}"
echo "=============================================="
echo ""
echo "  To start all challenge servers:"
echo "    ./start_sse_servers.sh"
echo ""
echo "  To start the MCP client (in a new terminal):"
echo "    ./venv/bin/python fixes/ollama_mcp_client.py"
echo ""
echo "  Challenge SSE endpoints:"
echo "    Challenge 1  →  http://localhost:9001/sse"
echo "    Challenge 2  →  http://localhost:9002/sse"
echo "    Challenge 3  →  http://localhost:9003/sse"
echo "    Challenge 4  →  http://localhost:9004/sse"
echo "    Challenge 5  →  http://localhost:9005/sse"
echo "    Challenge 6  →  http://localhost:9006/sse"
echo "    Challenge 7  →  http://localhost:9007/sse"
echo "    Challenge 8  →  http://localhost:9008/sse"
echo "    Challenge 9  →  http://localhost:9009/sse"
echo "    Challenge 10 →  http://localhost:9010/sse"
echo ""
