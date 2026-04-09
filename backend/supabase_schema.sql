-- ============================================================
-- PrepGenie - Supabase SQL Schema
-- Matched to backend data model (app.py + storage.py)
-- ============================================================


-- ============================================================
-- 1. PROFILES TABLE
--    Base user table, auto-populated via trigger on auth.users
-- ============================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role        TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'admin')),
    full_name   TEXT,
    email       TEXT,
    phone       TEXT,
    avatar_url  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;


-- ============================================================
-- 2. STUDENT_PROFILES TABLE
--    Extended profile + all PrepGenie agent output fields
--    Mirrors the student record saved by storage.py / upsert_student()
-- ============================================================
CREATE TABLE IF NOT EXISTS public.student_profiles (
    id                   UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,

    -- Coding platform handles
    github_username      TEXT,
    leetcode_username    TEXT,
    hackerrank_username  TEXT,
    resume_url           TEXT,

    -- Core PrepGenie fields (from generate-roadmap response)
    goal                 TEXT DEFAULT 'SDE',
    skills               JSONB DEFAULT '[]',          -- list of skill strings
    roadmap              JSONB DEFAULT '[]',          -- list of task objects {title, completed, missed, ...}
    status               TEXT DEFAULT 'Learning'
                             CHECK (status IN ('Learning', 'Ready', 'At Risk')),
    probability          NUMERIC(5,2) DEFAULT 0,      -- placement probability 0-100
    readiness_score      INTEGER DEFAULT 0,

    -- Agent outputs
    suggestions          JSONB DEFAULT '[]',          -- recommendation strings
    alerts               JSONB DEFAULT '[]',          -- alert strings
    alternative_careers  JSONB DEFAULT '[]',          -- career alternatives from strategist
    strategy             TEXT,                        -- strategy narrative
    explanation          TEXT,                        -- evaluator explanation

    -- Task tracking
    tasks_completed      INTEGER DEFAULT 0,
    tasks_missed         INTEGER DEFAULT 0,

    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.student_profiles ENABLE ROW LEVEL SECURITY;


-- ============================================================
-- 3. CHAT_MESSAGES TABLE
--    AI chat history per student
-- ============================================================
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;


-- ============================================================
-- 4. TRIGGER: Auto-create profile row on new auth.users signup
-- ============================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    -- Insert base profile
    INSERT INTO public.profiles (id, email, full_name, avatar_url, role)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        COALESCE(NEW.raw_user_meta_data->>'avatar_url', ''),
        COALESCE(NEW.raw_user_meta_data->>'role', 'student')
    )
    ON CONFLICT (id) DO NOTHING;

    -- Insert empty student profile row (so it's always present for students)
    INSERT INTO public.student_profiles (id)
    VALUES (NEW.id)
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();


-- ============================================================
-- 5. HELPER FUNCTION: Check if current user is admin
-- ============================================================
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.profiles
        WHERE id = auth.uid() AND role = 'admin'
    );
$$;


-- ============================================================
-- 6. ROW LEVEL SECURITY POLICIES
-- ============================================================

-- ---- profiles ----

-- Students can read their own profile
CREATE POLICY "student_read_own_profile"
    ON public.profiles
    FOR SELECT
    USING (auth.uid() = id);

-- Students can update their own profile
CREATE POLICY "student_update_own_profile"
    ON public.profiles
    FOR UPDATE
    USING (auth.uid() = id);

-- Admins can read all profiles
CREATE POLICY "admin_read_all_profiles"
    ON public.profiles
    FOR SELECT
    USING (public.is_admin());

-- Admins can update all profiles
CREATE POLICY "admin_update_all_profiles"
    ON public.profiles
    FOR UPDATE
    USING (public.is_admin());


-- ---- student_profiles ----

-- Students can read their own student profile
CREATE POLICY "student_read_own_student_profile"
    ON public.student_profiles
    FOR SELECT
    USING (auth.uid() = id);

-- Students can update their own student profile
CREATE POLICY "student_update_own_student_profile"
    ON public.student_profiles
    FOR UPDATE
    USING (auth.uid() = id);

-- Students can insert their own student profile
CREATE POLICY "student_insert_own_student_profile"
    ON public.student_profiles
    FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Admins can read all student profiles
CREATE POLICY "admin_read_all_student_profiles"
    ON public.student_profiles
    FOR SELECT
    USING (public.is_admin());

-- Admins can update all student profiles
CREATE POLICY "admin_update_all_student_profiles"
    ON public.student_profiles
    FOR UPDATE
    USING (public.is_admin());


-- ---- chat_messages ----

-- Students can read their own messages
CREATE POLICY "student_read_own_messages"
    ON public.chat_messages
    FOR SELECT
    USING (auth.uid() = student_id);

-- Students can insert their own messages
CREATE POLICY "student_insert_own_messages"
    ON public.chat_messages
    FOR INSERT
    WITH CHECK (auth.uid() = student_id);

-- Admins can read all messages
CREATE POLICY "admin_read_all_messages"
    ON public.chat_messages
    FOR SELECT
    USING (public.is_admin());


-- ============================================================
-- 7. INDEXES for performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_student_profiles_status
    ON public.student_profiles(status);

CREATE INDEX IF NOT EXISTS idx_student_profiles_probability
    ON public.student_profiles(probability DESC);

CREATE INDEX IF NOT EXISTS idx_chat_messages_student_id
    ON public.chat_messages(student_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_profiles_role
    ON public.profiles(role);


-- ============================================================
-- 8. UPDATED_AT auto-update trigger for student_profiles
-- ============================================================
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS set_student_profiles_updated_at ON public.student_profiles;
CREATE TRIGGER set_student_profiles_updated_at
    BEFORE UPDATE ON public.student_profiles
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
