-- =============================================
-- Add Google OAuth columns to users table
-- =============================================

ALTER TABLE users ADD COLUMN google_id TEXT UNIQUE;
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- Make password nullable (for OAuth users without password)
ALTER TABLE users MODIFY COLUMN password TEXT;
