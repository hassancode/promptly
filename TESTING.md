# Testing Guide - Promptly Authentication System

This guide walks you through testing the complete authentication flow end-to-end.

## Prerequisites

- Docker and Docker Compose installed
- Ports 3000, 5432, 6379, and 8000 available

## Quick Start - Full Stack Testing

### 1. Start All Services

```bash
# From the project root
docker-compose up --build
```

This will start:
- **PostgreSQL** (port 5432) - Database
- **Redis** (port 6379) - Session store
- **API** (port 8000) - FastAPI backend
- **Web** (port 3000) - Next.js frontend

Wait for all services to be healthy (check logs for "Application startup complete").

### 2. Run Database Migrations

```bash
# In a new terminal
cd apps/api
poetry run alembic upgrade head
```

This creates the `users` table in PostgreSQL.

### 3. Verify Services Are Running

```bash
# Check API health
curl http://localhost:8000/

# Expected response:
# {"status":"ok","message":"Promptly API is running"}

# Check API docs
open http://localhost:8000/docs
```

---

## Manual Testing - Authentication Flow

### Test 1: User Registration

**Using the Web UI:**
1. Open http://localhost:3000/register
2. Enter email: `test@example.com`
3. Enter password: `SecurePass123!`
4. Confirm password: `SecurePass123!`
5. Click "Create Account"

**Expected Result:**
- Success toast appears: "Account created! Please check your email..."
- Console shows verification email (MVP mode)
- Auto-redirect to /login after 3 seconds

**Verification Email in Console:**
```
============================================================
📧 VERIFICATION EMAIL (MVP - Not Actually Sent)
============================================================
To: test@example.com
From: noreply@promptly.com
Subject: Verify your Promptly account

Please verify your email by clicking this link:
http://localhost:3000/verify?token={VERIFICATION_TOKEN}
============================================================
```

**Using cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'

# Expected response:
# {
#   "id": "uuid-here",
#   "email": "test@example.com",
#   "verified": false,
#   "created_at": "2024-01-07T..."
# }
```

### Test 2: Email Verification

**Using the Web UI:**
1. Copy the verification token from the console logs
2. Visit: `http://localhost:3000/verify?token={TOKEN}`
3. Wait for verification to complete

**Expected Result:**
- Loading spinner appears
- Success message: "Email Verified Successfully!"
- Auto-redirect to /login after 3 seconds

**Using cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"token":"TOKEN_FROM_EMAIL"}'

# Expected response:
# {
#   "id": "uuid-here",
#   "email": "test@example.com",
#   "verified": true,
#   "created_at": "2024-01-07T..."
# }
```

### Test 3: User Login

**Using the Web UI:**
1. Visit http://localhost:3000/login
2. Enter email: `test@example.com`
3. Enter password: `SecurePass123!`
4. Click "Sign In"

**Expected Result:**
- Redirect to /dashboard
- Navigation shows user email
- "Logout" button visible
- Dashboard shows empty state with "Start New Analysis" button

**Using cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}' \
  -c cookies.txt

# Expected response:
# {
#   "id": "uuid-here",
#   "email": "test@example.com",
#   "verified": true,
#   "created_at": "2024-01-07T..."
# }

# Session cookie saved to cookies.txt
```

### Test 4: Protected Route Access

**Using the Web UI:**
1. While logged in, visit http://localhost:3000/dashboard
2. Dashboard should load with welcome message
3. Open new incognito window
4. Visit http://localhost:3000/dashboard directly

**Expected Result (Authenticated):**
- Dashboard loads with user email
- Shows "Start New Analysis" button

**Expected Result (Not Authenticated):**
- Redirect to /login
- No flash of dashboard content

**Using cURL:**
```bash
# With session cookie
curl http://localhost:8000/api/v1/auth/me \
  -b cookies.txt

# Expected response:
# {
#   "id": "uuid-here",
#   "email": "test@example.com",
#   "verified": true,
#   "created_at": "2024-01-07T..."
# }

# Without session cookie
curl http://localhost:8000/api/v1/auth/me

# Expected response:
# {"error": "Not authenticated", "status_code": 401}
```

### Test 5: User Logout

**Using the Web UI:**
1. While logged in, click "Logout" in navigation
2. Observe the redirect

**Expected Result:**
- Redirect to homepage (/)
- Navigation shows "Login" and "Sign Up" buttons
- Visiting /dashboard now redirects to /login

**Using cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -b cookies.txt

# Expected response:
# {"message": "Logged out successfully"}

# Verify session is cleared
curl http://localhost:8000/api/v1/auth/me \
  -b cookies.txt

# Expected response:
# {"error": "Invalid or expired session", "status_code": 401}
```

---

## Automated Testing

### Run Backend Tests

```bash
cd apps/api

# Run all tests
poetry run pytest tests/ -v

# Run contract tests only
poetry run pytest tests/contract/ -v

# Run integration tests only
poetry run pytest tests/integration/ -v

# Run unit tests only
poetry run pytest tests/unit/ -v

# Run with coverage
poetry run pytest tests/ --cov=src --cov-report=html
```

**Expected Results:**
- Unit tests: 8/8 passing
- Contract tests: 14/14 passing (with database running)
- Integration tests: 6/6 passing (with database running)
- OpenAPI tests: 14/14 passing

### Test Database Connectivity

```bash
cd apps/api

# Test database connection
poetry run python -c "
from src.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection successful!')
"

# Test Redis connection
poetry run python -c "
import asyncio
from src.core.redis import get_redis

async def test():
    redis = await get_redis()
    await redis.ping()
    print('Redis connection successful!')

asyncio.run(test())
"
```

---

## Common Issues and Solutions

### Issue: Port Already in Use

```bash
# Check what's using the port
lsof -i :8000  # API
lsof -i :3000  # Web
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Stop the process or use different ports in docker-compose.yml
```

### Issue: Database Connection Failed

```bash
# Check if PostgreSQL container is running
docker ps | grep postgres

# Check PostgreSQL logs
docker logs promptly-postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Issue: Migration Fails

```bash
# Check current migration status
cd apps/api
poetry run alembic current

# Reset database (development only!)
docker-compose down -v  # Removes volumes
docker-compose up -d postgres redis
poetry run alembic upgrade head
```

### Issue: Session Not Persisting

```bash
# Check Redis logs
docker logs promptly-redis

# Test Redis connection
docker exec -it promptly-redis redis-cli ping

# Clear all sessions (development only!)
docker exec -it promptly-redis redis-cli FLUSHALL
```

---

## Testing Checklist

- [ ] All Docker services start successfully
- [ ] Database migrations run without errors
- [ ] API health endpoint responds
- [ ] API documentation loads at /docs
- [ ] Frontend loads at http://localhost:3000
- [ ] User can register an account
- [ ] Verification email appears in console logs
- [ ] User can verify email with token
- [ ] User can log in with verified account
- [ ] Session cookie is set on login
- [ ] Dashboard loads for authenticated user
- [ ] Dashboard redirects to login when not authenticated
- [ ] User can log out successfully
- [ ] Session is cleared on logout
- [ ] All backend tests pass
- [ ] Form validation works correctly
- [ ] Error messages display properly
- [ ] Success toasts appear and auto-dismiss

---

## Performance Testing

### Load Test Registration Endpoint

```bash
# Install apache bench
brew install apache2  # macOS

# Test registration endpoint
ab -n 100 -c 10 -p register.json -T application/json \
  http://localhost:8000/api/v1/auth/register

# Where register.json contains:
# {"email":"loadtest@example.com","password":"SecurePass123!"}
```

### Monitor Redis Sessions

```bash
# Watch session creation in real-time
docker exec -it promptly-redis redis-cli MONITOR

# Count active sessions
docker exec -it promptly-redis redis-cli --scan --pattern 'session:*' | wc -l

# View a session
docker exec -it promptly-redis redis-cli GET 'session:SESSION_ID_HERE'
```

---

## Clean Up

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes database data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

---

## Next Steps

After verifying authentication works:
1. Test with different browsers
2. Test with network throttling (slow 3G)
3. Test concurrent user registrations
4. Test session expiration (default: 7 days)
5. Proceed to Phase 4: Brand and Competitor Setup
