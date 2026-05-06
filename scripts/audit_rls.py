#!/usr/bin/env python3
"""
RLS Audit — checks every table in the public schema for missing Row Level Security.

Usage:
    python scripts/audit_rls.py

Requirements:
    SUPABASE_DB_URL env var (or in ~/.webiascrap_supabase_config).
    Format: postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres
    Get it from: Supabase Dashboard → Settings → Database → Connection string → URI

Exit codes:
    0 — all tables have RLS enabled
    1 — one or more tables are missing RLS (also prints which ones)
"""

import os
import sys

import socket
import urllib.parse

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 not found. Run: pip install psycopg2-binary")
    sys.exit(2)


def parse_conn_params(db_url):
    """Parse a PostgreSQL URL into explicit connection params, forcing IPv4.
    Handles usernames with dots (e.g. postgres.projectref) that psycopg2 truncates."""
    parsed = urllib.parse.urlparse(db_url)
    hostname = parsed.hostname
    port = parsed.port or 5432
    try:
        ipv4 = socket.getaddrinfo(hostname, port, socket.AF_INET)[0][4][0]
    except (socket.gaierror, IndexError):
        ipv4 = hostname
    return {
        "host": ipv4,
        "port": port,
        "user": urllib.parse.unquote(parsed.username or ""),
        "password": urllib.parse.unquote(parsed.password or ""),
        "dbname": parsed.path.lstrip("/"),
        "sslmode": "require",
    }


COLORS = {
    "red":    "\033[91m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "blue":   "\033[94m",
    "reset":  "\033[0m",
}

def c(color, text):
    return f"{COLORS[color]}{text}{COLORS['reset']}"


def load_db_url():
    url = os.environ.get("SUPABASE_DB_URL")
    if url:
        return url

    config_path = os.path.expanduser("~/.webiascrap_supabase_config")
    if os.path.exists(config_path):
        cfg = {}
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    cfg[k.strip()] = v.strip()
        if "SUPABASE_DB_URL" in cfg:
            return cfg["SUPABASE_DB_URL"]

    print(c("red", "ERROR: SUPABASE_DB_URL not found."))
    print("Set it as an env var or add it to ~/.webiascrap_supabase_config")
    print()
    print("How to get it:")
    print("  Supabase Dashboard → Settings → Database → Connection string → URI")
    print("  Format: postgresql://postgres:<password>@db.<ref>.supabase.co:5432/postgres")
    sys.exit(2)


TABLES_WITHOUT_RLS_SQL = """
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
  AND rowsecurity = false
ORDER BY tablename;
"""

TABLES_WITH_RLS_SQL = """
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
  AND rowsecurity = true
ORDER BY tablename;
"""

POLICIES_SQL = """
SELECT tablename, policyname, cmd, roles::text
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
"""

TABLES_WITHOUT_POLICIES_SQL = """
SELECT t.tablename
FROM pg_tables t
WHERE t.schemaname = 'public'
  AND t.rowsecurity = true
  AND NOT EXISTS (
      SELECT 1 FROM pg_policies p
      WHERE p.schemaname = 'public'
        AND p.tablename = t.tablename
  )
ORDER BY t.tablename;
"""


def run_audit(db_url):
    print(c("blue", "═" * 60))
    print(c("blue", "  WebIAScrap — Supabase RLS Security Audit"))
    print(c("blue", "═" * 60))
    print()

    try:
        conn = psycopg2.connect(**parse_conn_params(db_url))
        conn.set_session(readonly=True, autocommit=True)
        cur = conn.cursor()
    except Exception as e:
        print(c("red", f"Connection failed: {e}"))
        sys.exit(2)

    issues = []

    # 1. Tables with RLS disabled
    cur.execute(TABLES_WITHOUT_RLS_SQL)
    no_rls = [row[0] for row in cur.fetchall()]

    if no_rls:
        print(c("red", f"❌  RLS DISABLED ({len(no_rls)} tables):"))
        for t in no_rls:
            print(f"     • public.{t}")
            issues.append(f"public.{t}: RLS not enabled")
    else:
        print(c("green", "✅  RLS enabled on all public tables"))

    print()

    # 2. Tables with RLS enabled but zero policies (default-deny is intentional, flag as info)
    cur.execute(TABLES_WITHOUT_POLICIES_SQL)
    no_policies = [row[0] for row in cur.fetchall()]

    if no_policies:
        print(c("yellow", f"ℹ️   RLS enabled, no policies (default-deny) — verify intent:"))
        for t in no_policies:
            print(f"     • public.{t}")
    print()

    # 3. Full policy listing
    cur.execute(POLICIES_SQL)
    policies = cur.fetchall()

    if policies:
        print(c("blue", "Active policies:"))
        current_table = None
        for tablename, policyname, cmd, roles in policies:
            if tablename != current_table:
                print(f"  public.{tablename}")
                current_table = tablename
            print(f"    [{cmd}] {policyname}  →  roles: {roles}")
    else:
        print(c("yellow", "No active policies found."))

    print()
    cur.close()
    conn.close()

    # Summary
    print(c("blue", "─" * 60))
    if issues:
        print(c("red", f"AUDIT FAILED — {len(issues)} issue(s) found:"))
        for issue in issues:
            print(f"  • {issue}")
        print()
        print("Fix: run migrations/005_enable_rls_security.sql in Supabase SQL Editor")
        print(c("blue", "─" * 60))
        sys.exit(1)
    else:
        print(c("green", "AUDIT PASSED — no security issues found"))
        print(c("blue", "─" * 60))
        sys.exit(0)


if __name__ == "__main__":
    db_url = load_db_url()
    run_audit(db_url)
