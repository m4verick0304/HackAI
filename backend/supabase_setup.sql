/**
 * Supabase Database Setup for PrepGenie
 * Run this SQL in the Supabase SQL Editor to create all tables and RLS policies
 */

-- ══════════════════════════════════════════════════════════════════════════════
-- 1. CREATE PROFILES TABLE (extends auth.users)
-- ══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT,
  full_name TEXT,
  role TEXT CHECK (role IN ('student', 'admin', 'tpc')) DEFAULT 'student',
  avatar_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- RLS: Users can read their own profile
CREATE POLICY profiles_self_read ON profiles
  FOR SELECT USING (auth.uid() = id);

-- RLS: Users can update their own profile
CREATE POLICY profiles_self_update ON profiles
  FOR UPDATE USING (auth.uid() = id);

-- RLS: Admins can read all profiles
CREATE POLICY profiles_admin_read ON profiles
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
    )
  );

-- ══════════════════════════════════════════════════════════════════════════════
-- 2. CREATE STUDENTS TABLE (main data store)
-- ══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS students (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  email TEXT,
  goal TEXT DEFAULT 'SDE',
  skills TEXT[] DEFAULT '{}',
  
  -- Roadmap & Progress
  roadmap JSONB DEFAULT '[]',
  tasks_completed INT DEFAULT 0,
  tasks_missed INT DEFAULT 0,
  
  -- Status & Scoring
  status TEXT DEFAULT 'Learning' CHECK (status IN ('Ready', 'Learning', 'At Risk')),
  probability INT DEFAULT 0,
  
  -- AI Outputs
  suggestions TEXT[] DEFAULT '{}',
  alerts TEXT[] DEFAULT '{}',
  alternative_careers JSONB DEFAULT '[]',
  strategy TEXT,
  explanation TEXT,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE students ENABLE ROW LEVEL SECURITY;

-- RLS: Students can read their own record
CREATE POLICY students_self_read ON students
  FOR SELECT USING (auth.uid() = user_id);

-- RLS: Students can update their own record
CREATE POLICY students_self_update ON students
  FOR UPDATE USING (auth.uid() = user_id);

-- RLS: Students can insert their own record
CREATE POLICY students_self_insert ON students
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- RLS: Admins can read all students
CREATE POLICY students_admin_read ON students
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
    )
  );

-- RLS: Admins can update all students
CREATE POLICY students_admin_update ON students
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
    )
  );

-- ══════════════════════════════════════════════════════════════════════════════
-- 3. CREATE ACTIVITY_LOGS TABLE
-- ══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS activity_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  student_id UUID REFERENCES students(id) ON DELETE CASCADE,
  action TEXT NOT NULL,
  details JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

-- RLS: Users can read their own logs
CREATE POLICY activity_logs_self_read ON activity_logs
  FOR SELECT USING (auth.uid() = user_id);

-- RLS: Admins can read all logs
CREATE POLICY activity_logs_admin_read ON activity_logs
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid() AND profiles.role = 'admin'
    )
  );

-- ══════════════════════════════════════════════════════════════════════════════
-- 4. CREATE JOB_DESCRIPTIONS TABLE (for placement matching)
-- ══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS job_descriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  company TEXT NOT NULL,
  description TEXT,
  required_skills TEXT[] DEFAULT '{}',
  match_score INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE job_descriptions ENABLE ROW LEVEL SECURITY;

-- RLS: Anyone can read jobs (public)
CREATE POLICY job_descriptions_read ON job_descriptions
  FOR SELECT USING (true);

-- ══════════════════════════════════════════════════════════════════════════════
-- 5. CREATE INDEXES for performance
-- ══════════════════════════════════════════════════════════════════════════════
CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id);
CREATE INDEX IF NOT EXISTS idx_students_goal ON students(goal);
CREATE INDEX IF NOT EXISTS idx_students_status ON students(status);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_student_id ON activity_logs(student_id);

-- ══════════════════════════════════════════════════════════════════════════════
-- 6. INSERT SAMPLE JOB DESCRIPTIONS
-- ══════════════════════════════════════════════════════════════════════════════
INSERT INTO job_descriptions (title, company, description, required_skills) VALUES
('Software Engineer', 'Google', 'Looking for talented SDE', ARRAY['python', 'dsa', 'system design', 'sql']),
('Backend Developer', 'Amazon', 'Build scalable services', ARRAY['nodejs', 'sql', 'docker', 'aws']),
('Data Analyst', 'Flipkart', 'Analysis and insights', ARRAY['sql', 'excel', 'python', 'tableau']),
('ML Engineer', 'Microsoft', 'ML pipeline development', ARRAY['python', 'machine learning', 'tensorflow', 'sql']),
('Frontend Developer', 'Airbnb', 'React and UI development', ARRAY['react', 'javascript', 'html', 'css', 'typescript'])
ON CONFLICT DO NOTHING;

-- ══════════════════════════════════════════════════════════════════════════════
-- 7. CREATE FUNCTIONS FOR CONVENIENCE
-- ══════════════════════════════════════════════════════════════════════════════

-- Function to log student activity
CREATE OR REPLACE FUNCTION log_student_activity(
  p_user_id UUID,
  p_student_id UUID,
  p_action TEXT,
  p_details JSONB DEFAULT '{}'
) RETURNS void AS $$
BEGIN
  INSERT INTO activity_logs (user_id, student_id, action, details)
  VALUES (p_user_id, p_student_id, p_action, p_details);
END;
$$ LANGUAGE plpgsql;

-- Function to update student timestamp
CREATE OR REPLACE FUNCTION update_student_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update timestamp
CREATE TRIGGER students_update_timestamp
  BEFORE UPDATE ON students
  FOR EACH ROW
  EXECUTE FUNCTION update_student_timestamp();

-- Similar trigger for profiles
CREATE OR REPLACE FUNCTION update_profile_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_update_timestamp
  BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_profile_timestamp();
