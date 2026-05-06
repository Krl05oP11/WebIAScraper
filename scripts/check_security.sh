#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# check_security.sh — RLS audit for Supabase
#
# Run before every deployment or table migration.
# Requires SUPABASE_DB_URL in env or in ~/.webiascrap_supabase_config.
#
# Usage:
#   bash scripts/check_security.sh
#   ./scripts/check_security.sh          # if executable
#
# How to get SUPABASE_DB_URL:
#   Supabase Dashboard → Settings → Database → Connection string → URI
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${YELLOW}🔒 Running RLS security audit...${NC}"
echo ""

# Activate venv if present
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

python "$SCRIPT_DIR/audit_rls.py"
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Security check passed. Safe to deploy.${NC}"
elif [ $EXIT_CODE -eq 1 ]; then
    echo -e "${RED}❌ Security check FAILED. Fix RLS issues before deploying.${NC}"
    echo -e "${RED}   Apply: migrations/005_enable_rls_security.sql in Supabase SQL Editor${NC}"
    exit 1
else
    echo -e "${RED}❌ Audit script error (missing dependency or bad connection URL).${NC}"
    exit 2
fi
