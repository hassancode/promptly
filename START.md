# Quick Start Guide - Promptly

Get the Promptly authentication system up and running in 5 minutes.

## Step 1: Start Services (2 minutes)

```bash
# From project root
docker-compose up --build
```

**Wait for these messages:**
- ✓ `promptly-postgres | database system is ready to accept connections`
- ✓ `promptly-redis | Ready to accept connections`
- ✓ `promptly-api | Application startup complete`
- ✓ `promptly-web | ✓ Ready in ...`

## Step 2: Run Database Migration (30 seconds)

**In a new terminal:**

```bash
cd apps/api
poetry run alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 18c7abce0848, create users table
```

## Step 3: Test the System (2 minutes)

### Option A: Web UI Testing

1. **Open Browser**: http://localhost:3000

2. **Register Account:**
   - Click "Get Started Free"
   - Email: `demo@example.com`
   - Password: `SecurePass123!`
   - Click "Create Account"
   - ✓ Success toast appears
   - ✓ Check terminal for verification email

3. **Verify Email:**
   - Copy token from terminal logs
   - Visit: `http://localhost:3000/verify?token=YOUR_TOKEN`
   - ✓ Success message appears
   - ✓ Auto-redirect to login

4. **Login:**
   - Email: `demo@example.com`
   - Password: `SecurePass123!`
   - Click "Sign In"
   - ✓ Redirects to dashboard
   - ✓ Shows your email in nav

5. **Test Protected Route:**
   - You should see the dashboard with "Start New Analysis" button
   - Open incognito window
   - Try to visit: http://localhost:3000/dashboard
   - ✓ Should redirect to /login

6. **Logout:**
   - Click "Logout" button in nav
   - ✓ Redirects to homepage
   - ✓ Nav shows "Login" and "Sign Up" again

### Option B: API Testing with cURL

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"api@example.com","password":"SecurePass123!"}'

# Copy the verification token from API logs

# 2. Verify Email
curl -X POST http://localhost:8000/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"token":"YOUR_TOKEN_HERE"}'

# 3. Login (saves cookie)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"api@example.com","password":"SecurePass123!"}' \
  -c cookies.txt

# 4. Access Protected Route
curl http://localhost:8000/api/v1/auth/me -b cookies.txt

# 5. Logout
curl -X POST http://localhost:8000/api/v1/auth/logout -b cookies.txt
```

## Step 4: Run Automated Tests

```bash
cd apps/api

# Quick tests (no database needed)
./test_quick.sh

# Full integration tests (requires services running)
poetry run pytest tests/ -v

# Expected: 22 tests passing
```

---

## Verification Checklist

- [ ] All 4 Docker containers running
- [ ] Database migration completed
- [ ] Can register a new account
- [ ] Verification email appears in logs
- [ ] Can verify email with token
- [ ] Can login with credentials
- [ ] Dashboard loads when authenticated
- [ ] Dashboard redirects to login when not authenticated
- [ ] Can logout successfully
- [ ] All 22 automated tests pass

---

## Common Issues

### "Address already in use"
```bash
# Check what's using the ports
lsof -i :3000  # Next.js
lsof -i :8000  # FastAPI
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Kill the process or stop existing containers
docker-compose down
```

### "Poetry command not found"
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or use pip
python3 -m pip install --user poetry
```

### "Docker not found"
```bash
# Install Docker Desktop
# macOS: https://www.docker.com/products/docker-desktop
# Or install via Homebrew:
brew install --cask docker
```

---

## What's Working

✅ **Backend (FastAPI):**
- User registration with email validation
- Email verification system (console logs for MVP)
- Secure password hashing (bcrypt)
- Session management (Redis-backed)
- Protected API endpoints
- Comprehensive error handling
- Structured JSON logging

✅ **Frontend (Next.js):**
- Registration page with validation
- Login page with auth state
- Email verification page
- Protected dashboard
- Navigation with auth state
- Error/success toasts
- Form validation

✅ **Database:**
- PostgreSQL with Alembic migrations
- User model with email verification
- Proper indexing for performance

✅ **Testing:**
- 8 unit tests (session store)
- 14 OpenAPI contract tests
- 14 auth endpoint tests
- 6 integration tests for auth flows

---

## Next Steps

Once authentication is working:
1. Explore the API documentation: http://localhost:8000/docs
2. Test with multiple users
3. Check Redis sessions: `docker exec -it promptly-redis redis-cli KEYS "session:*"`
4. Monitor logs: `docker-compose logs -f api`
5. Ready for Phase 4: Brand & Competitor Setup

---

## Stop Services

```bash
# Stop containers (keeps data)
docker-compose down

# Stop and remove data
docker-compose down -v
```

---

**Need help?** Check `TESTING.md` for detailed testing scenarios.
