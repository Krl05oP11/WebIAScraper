-- ============================================================
-- TEMPLATE: New table migration
-- Copy this file, rename it NNN_create_TABLENAME.sql,
-- and fill in the sections marked with <REPLACE>.
-- ============================================================
-- Migration: Create <TABLENAME> table
-- Date: <YYYY-MM-DD>
-- Description: <what this table stores and why>

-- ── 1. Create table ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.<tablename> (
    id      SERIAL PRIMARY KEY,
    -- <add your columns here>
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── 2. Indexes ────────────────────────────────────────────────────────────────
-- CREATE INDEX IF NOT EXISTS idx_<tablename>_<column> ON public.<tablename>(<column>);

-- ── 3. Row Level Security (MANDATORY for every new table) ─────────────────────
-- RLS must be enabled before the table is accessible via PostgREST.
-- Flask (service role / direct PostgreSQL) bypasses RLS → app logic unaffected.
-- Choose ONE of the three patterns below and delete the others:

-- PATTERN A — Internal only (e.g. admin tables, credentials, staging queues)
-- No policies = PostgREST access completely blocked. Service role still works.
ALTER TABLE public.<tablename> ENABLE ROW LEVEL SECURITY;

-- PATTERN B — Public read, no writes via PostgREST (e.g. public content)
-- ALTER TABLE public.<tablename> ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "<tablename>_select_public"
--   ON public.<tablename>
--   FOR SELECT TO anon, authenticated
--   USING (true);

-- PATTERN C — Authenticated users see only their own rows
-- ALTER TABLE public.<tablename> ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "<tablename>_select_own"
--   ON public.<tablename>
--   FOR SELECT TO authenticated
--   USING (auth.uid() = user_id);
-- CREATE POLICY "<tablename>_insert_own"
--   ON public.<tablename>
--   FOR INSERT TO authenticated
--   WITH CHECK (auth.uid() = user_id);

-- ── 4. Comments ───────────────────────────────────────────────────────────────
COMMENT ON TABLE public.<tablename> IS '<description of the table purpose>';

-- ── 5. Verification ───────────────────────────────────────────────────────────
-- Run after applying: confirm rowsecurity = true for this table
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND tablename = '<tablename>';
