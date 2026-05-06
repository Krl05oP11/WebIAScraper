-- Migration: Enable Row Level Security on all public schema tables
-- Date: 2026-05-06
-- Context: Supabase Security Advisor flagged public.noticias and public.users for missing RLS.
--          Flask connects via direct PostgreSQL (service role) which bypasses RLS entirely,
--          so enabling RLS here only affects PostgREST (the public REST API layer).

-- ── noticias ──────────────────────────────────────────────────────────────────
-- News content is public-facing; the website reads it. Allow SELECT via PostgREST.
-- All writes come from Flask (service role) → RLS has no effect on writes.
ALTER TABLE public.noticias ENABLE ROW LEVEL SECURITY;

CREATE POLICY "noticias_select_public"
  ON public.noticias
  FOR SELECT
  TO anon, authenticated
  USING (true);

-- ── users ─────────────────────────────────────────────────────────────────────
-- Contains bcrypt password hashes. Must be completely invisible via PostgREST.
-- Flask reads via direct PostgreSQL (service role) → authentication unaffected.
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
-- Intentionally no SELECT/INSERT/UPDATE/DELETE policy: default-deny for PostgREST.

-- ── apublicar ─────────────────────────────────────────────────────────────────
-- Internal staging table. Not exposed publicly. Default-deny for PostgREST.
ALTER TABLE public.apublicar ENABLE ROW LEVEL SECURITY;
-- Intentionally no policies.

-- Verification: expected rowsecurity = true for all three tables
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
