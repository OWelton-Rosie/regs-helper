#!/bin/bash

set -e

echo "========================================"
echo " regs-helper setup"
echo "========================================"
echo

# -------------------------
# Check Python
# -------------------------

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')

echo "Found Python $PYTHON_VERSION"

# Require Python 3.13+
python3 - <<'PY'
import sys

if sys.version_info < (3, 13):
    print("Error: Python 3.13 or newer is required.")
    sys.exit(1)
PY

# -------------------------
# Check Node
# -------------------------

if ! command -v node >/dev/null 2>&1; then
    echo "Error: Node.js is not installed."
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "Error: npm is not installed."
    exit 1
fi

echo "Found Node.js $(node --version)"
echo "Found npm $(npm --version)"
echo

# -------------------------
# Python virtual environment
# -------------------------

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "Python virtual environment already exists."
fi

echo "Installing Python dependencies..."
./venv/bin/python -m pip install --upgrade pip
./venv/bin/python -m pip install -r requirements.txt

echo

# -------------------------
# Frontend dependencies
# -------------------------

echo "Installing frontend dependencies..."

cd frontend
npm install
cd ..

echo

# -------------------------
# Environment files
# -------------------------

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env from .env.example"
    else
        echo "Warning: .env.example not found."
    fi
else
    echo ".env already exists; leaving it unchanged."
fi

if [ ! -f "frontend/.env" ]; then
    if [ -f "frontend/.env.example" ]; then
        cp frontend/.env.example frontend/.env
        echo "Created frontend/.env from frontend/.env.example"
    else
        echo "Warning: frontend/.env.example not found."
    fi
else
    echo "frontend/.env already exists; leaving it unchanged."
fi

echo
echo "========================================"
echo " Setup complete!"
echo "========================================"
echo
echo "Before starting the app, make sure .env"
echo "contains your required configuration."
echo
echo "Start the backend:"
echo
echo "    source venv/bin/activate"
echo "    uvicorn app:app --reload"
echo
echo "Then, in another terminal:"
echo
echo "    cd frontend"
echo "    npm run dev"
echo