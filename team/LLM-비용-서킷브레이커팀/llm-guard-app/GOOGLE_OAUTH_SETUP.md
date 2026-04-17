# Google OAuth Setup Guide

## Overview
This implementation adds Google OAuth authentication to llm-guard-app, allowing users to sign in with their Google accounts.

## Implementation Summary

### 1. Database Schema Changes
**Migration File:** `d1-migrations/002_add_google_oauth.sql`

Added columns to `users` table:
- `google_id TEXT UNIQUE` - Google user ID (for linking accounts)
- `avatar_url TEXT` - User's Google profile picture
- Made `password` nullable (OAuth users don't need passwords)

### 2. New API Routes

#### `GET /api/auth/google`
Initiates Google OAuth flow. Redirects user to Google consent screen.
- Generates authorization request with proper scopes
- Uses configured redirect URI

#### `GET /api/auth/google/callback`
Handles Google OAuth callback after user consent.
- Exchanges authorization code for access token
- Fetches user info from Google
- Creates new user or links existing user
- Issues JWT token and sets HttpOnly cookie
- Redirects to dashboard on success

### 3. Code Changes

#### `src/lib/auth.ts`
- Updated `User` interface to include `google_id` and `avatar_url`
- Added `getUserByGoogleId()` function for OAuth lookups
- Updated all user SELECT queries to include new columns

#### `src/app/api/auth/login/route.ts` & `signup/route.ts`
- Changed cookie `sameSite` from `'strict'` to `'lax'`
- **Reason:** OAuth redirects require `lax` SameSite policy. `strict` would drop cookies on cross-site redirects from Google

#### `.env.example`
- Added `GOOGLE_CLIENT_ID`
- Added `GOOGLE_CLIENT_SECRET`

## Setup Instructions

### Step 1: Create Google OAuth Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable OAuth 2.0 Consent Screen:
   - User type: External
   - Add required scopes: `email`, `profile`, `openid`
4. Create OAuth 2.0 credentials:
   - Type: Web application
   - Authorized redirect URIs:
     - `http://localhost:3000/api/auth/google/callback` (development)
     - `https://llm-guard-app.lian1803.workers.dev/api/auth/google/callback` (production)
     - Any other deployment URLs

### Step 2: Add Credentials to Environment
```bash
# .env.local or Vercel environment variables
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
NEXT_PUBLIC_APP_URL=https://your-deployment-url.com
```

### Step 3: Run Database Migration
```bash
# Option 1: Python (cross-platform)
python scripts/run-migration.py

# Option 2: Bash
bash scripts/run-migration.sh
```

Or manually execute in Cloudflare D1:
```sql
ALTER TABLE users ADD COLUMN google_id TEXT UNIQUE;
ALTER TABLE users ADD COLUMN avatar_url TEXT;
```

### Step 4: Test OAuth Flow
1. Start development server: `npm run dev`
2. Visit login page
3. Click "Sign in with Google"
4. Complete Google consent
5. Should be redirected to dashboard with JWT cookie set

## Key Features

### User Linking
- If user signs in with Google using email that already exists → links to existing account
- Updates `google_id` and `avatar_url`
- First sign-in with new email → creates new user with plan='free'

### JWT Integration
- Uses existing JWT system (`src/lib/auth.ts`)
- Google OAuth token is exchanged for internal JWT
- JWT stored in HttpOnly cookie for security

### SameSite Cookie Policy
- Changed from `strict` to `lax` to support OAuth redirects
- Still provides CSRF protection for most scenarios
- More compatible with OAuth 2.0 redirect flows

### Error Handling
- User denies consent → redirected to login with error parameter
- Token exchange fails → error page
- User info fetch fails → error page
- All errors include `requestId` for logging

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/google` | GET | Initiate OAuth flow |
| `/api/auth/google/callback` | GET | Handle OAuth callback |
| `/api/auth/login` | POST | Password-based login |
| `/api/auth/signup` | POST | Password-based signup |
| `/api/auth/signout` | POST | Logout (clears cookie) |

## Database Schema (users table)

```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  password TEXT,                      -- NULL for OAuth users
  google_id TEXT UNIQUE,               -- NEW: Google user ID
  avatar_url TEXT,                     -- NEW: Profile picture URL
  plan TEXT NOT NULL DEFAULT 'free',
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

## Security Considerations

1. **HTTPS Required:** OAuth redirects must use HTTPS in production
2. **Secret Storage:** Keep `GOOGLE_CLIENT_SECRET` in server-side environment only
3. **CSRF:** SameSite=lax provides protection against CSRF attacks
4. **JWT Expiration:** Tokens expire after 7 days (configurable in auth.ts)
5. **HttpOnly Cookies:** Prevents XSS attacks from stealing tokens
6. **Timing Attacks:** Password verification uses constant-time comparison

## Troubleshooting

### "Invalid redirect_uri"
- Check that redirect URI in code matches Google Console configuration
- Ensure NEXT_PUBLIC_APP_URL is set correctly

### "Cookie not being set"
- Verify browser allows third-party cookies
- Check that secure flag matches environment (http vs https)
- Verify SameSite=lax on cookie

### "User info fetch fails"
- Check that access token is valid
- Verify Google API is enabled
- Check for quota limits on Google Cloud project

### "User already exists with this email"
- Different auth method was used previously
- OAuth linking should handle this (update google_id)
- Check callback logic

## Related Files

- `src/app/api/auth/google/route.ts` - OAuth initiation
- `src/app/api/auth/google/callback/route.ts` - OAuth callback
- `src/lib/auth.ts` - Core auth functions
- `src/lib/auth-middleware.ts` - Request authentication
- `d1-migrations/002_add_google_oauth.sql` - Database migration
- `scripts/run-migration.py` - Migration runner

## Testing Checklist

- [ ] Google OAuth credentials created
- [ ] Environment variables set
- [ ] Database migration applied
- [ ] Development server starts without errors
- [ ] OAuth initiation redirects to Google
- [ ] Google consent screen appears
- [ ] After consent, redirected to dashboard
- [ ] User created in database with google_id
- [ ] Auth cookie set in browser
- [ ] Dashboard API calls succeed with cookie
- [ ] Existing email linking works
- [ ] Error handling works for denied consent

## Next Steps

1. **Frontend Integration:** Add "Sign in with Google" button to login page
2. **User Profile:** Display avatar_url in user profile
3. **Account Linking:** Add option to link/unlink OAuth accounts
4. **Logout:** Ensure signout clears cookies properly
5. **Session Refresh:** Consider implementing token refresh before expiry
6. **Analytics:** Track OAuth vs password signups
