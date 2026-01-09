# Phase 6 SSE Streaming - Testing Guide

Complete guide for testing the Phase 6 Multi-Provider AI Querying and SSE Streaming implementation.

## 📋 Prerequisites

Before testing, ensure you have:

1. **Database running** (PostgreSQL)
   ```bash
   # Option A: Docker
   docker-compose up postgres -d

   # Option B: Native
   brew services start postgresql@16  # macOS
   sudo systemctl start postgresql   # Linux
   ```

2. **Redis running**
   ```bash
   # Option A: Docker
   docker-compose up redis -d

   # Option B: Native
   brew services start redis  # macOS
   sudo systemctl start redis # Linux
   ```

3. **Dependencies installed**
   ```bash
   cd apps/api
   poetry install  # or pip install -r requirements.txt
   ```

4. **Migration applied**
   ```bash
   cd apps/api
   poetry run alembic upgrade head
   ```

## 🧪 Test Suite Options

### Option 1: Unit Tests (No Server Required)

Test the core logic without starting the API server:

```bash
cd apps/api
python3 test_sse_streaming.py
```

**What it tests:**
- ✅ Provider adapter initialization
- ✅ Mock query execution (OpenAI, Claude)
- ✅ Concurrent query orchestration
- ✅ SSE event schema validation
- ✅ Progress tracking
- ✅ Citation extraction
- ✅ Provider enable/disable configuration

**Expected output:**
```
================================================================================
🧪 PHASE 6 SSE STREAMING TEST SUITE
================================================================================
...
📊 TEST SUMMARY
================================================================================
  ✅ PASS Provider Adapters
  ✅ PASS SSE Event Generation
  ✅ PASS Provider Orchestrator

Total: 3/3 tests passed

🎉 All tests passed! Phase 6 core infrastructure is working.
```

### Option 2: Integration Test (Server Required)

Test the actual SSE endpoint with a running server:

**Step 1: Start the API server**
```bash
cd apps/api
poetry run uvicorn src.main:app --reload --port 8000
```

**Step 2: Run the integration test**
```bash
cd apps/api
./test_sse_curl.sh
```

**What it tests:**
- ✅ User registration and authentication
- ✅ Analysis creation
- ✅ Competitor addition
- ✅ Prompt addition
- ✅ SSE streaming endpoint
- ✅ Real-time event delivery
- ✅ Provider query execution
- ✅ Progress updates

**Expected output:**
```
=========================================
SSE Streaming Endpoint Test
=========================================

📡 Checking if API is running...
   ✓ API is running

👤 Setting up test user...
   Email: sse-test-1704729600@example.com
   ✓ Registration successful
   ✓ Login successful

📊 Creating test analysis...
   ✓ Analysis created: abc123...

🏁 Adding competitors...
   ✓ Added: Rivian
   ✓ Added: Lucid Motors

❓ Adding prompts...
   ✓ Added prompt
   ✓ Added prompt

=========================================
🔴 TESTING SSE STREAMING
=========================================

Connecting to SSE stream...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 Event: progress_update
📦 Data: {
  "completed": 0,
  "total": 4,
  "percentage": 0.0
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 Event: provider_started
📦 Data: {
  "provider": "openai",
  "prompt_id": "...",
  "timestamp": "2026-01-08T..."
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 Event: provider_completed
📦 Data: {
  "provider": "openai",
  "response_id": "...",
  "has_citations": true,
  "citation_count": 2
}
...
```

### Option 3: Manual Testing with curl

Test individual components manually:

**1. Check API health:**
```bash
curl http://localhost:8000/
```

**2. Register a user:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

**3. Login and save cookie:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}' \
  -c cookies.txt
```

**4. Create analysis:**
```bash
curl -X POST http://localhost:8000/api/v1/analyses \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"brand_name":"Tesla"}'
```

**5. Add competitors:**
```bash
# Replace {analysis_id} with actual ID from step 4
curl -X POST http://localhost:8000/api/v1/analyses/{analysis_id}/competitors \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"competitor_name":"Rivian"}'
```

**6. Add prompts:**
```bash
curl -X POST http://localhost:8000/api/v1/analyses/{analysis_id}/prompts \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"prompt_text":"What are the best electric vehicles?"}'
```

**7. Stream SSE events:**
```bash
curl -N http://localhost:8000/api/v1/analyses/{analysis_id}/stream \
  -b cookies.txt
```

## 🔍 What to Look For

### Successful SSE Stream

You should see these event types in order:

1. **progress_update** - Initial progress (0%)
2. **provider_started** - For each enabled provider
3. **provider_completed** or **provider_failed** - As each provider finishes
4. **progress_update** - After each provider completes
5. **analysis_complete** - Final event with summary

### Provider Configuration

Test different provider configurations by editing `.env`:

**Test 1: All providers enabled (default)**
```bash
ENABLED_PROVIDERS=openai,claude,gemini,perplexity,google_ai,huggingface
```

**Test 2: Only two providers**
```bash
ENABLED_PROVIDERS=openai,claude
```

**Test 3: Single provider**
```bash
ENABLED_PROVIDERS=openai
```

After changing `.env`, restart the server and verify:
- Only enabled providers are queried
- Progress total = (prompts × enabled providers)
- SSE events only for enabled providers

### Mock Mode Testing

If no API keys are configured, providers run in mock mode:

```bash
# Remove all API keys from .env
#OPENAI_API_KEY=
#ANTHROPIC_API_KEY=

# Start server
poetry run uvicorn src.main:app --reload
```

**Expected behavior:**
- Providers still execute queries
- Mock responses are generated
- Mock citations are included
- SSE streaming works normally

## 🐛 Troubleshooting

### Issue: "No module named 'anthropic'"

**Solution:**
```bash
cd apps/api
poetry add anthropic
# or
pip install anthropic
```

### Issue: "No module named 'openai'"

**Solution:**
```bash
cd apps/api
poetry add openai
# or
pip install openai
```

### Issue: SSE stream disconnects immediately

**Possible causes:**
1. Analysis doesn't exist or user doesn't own it
2. No prompts added to analysis
3. Database connection lost

**Debug:**
```bash
# Check API logs
tail -f logs/api.log

# Verify analysis exists
curl http://localhost:8000/api/v1/analyses/{id} -b cookies.txt
```

### Issue: All providers fail

**Possible causes:**
1. No API keys configured (should use mock mode)
2. Network issues
3. Rate limiting

**Debug:**
Check provider status in logs:
```bash
grep "Provider.*query" logs/api.log
```

### Issue: Migration fails

**Solution:**
```bash
# Check current migration
poetry run alembic current

# If behind, upgrade
poetry run alembic upgrade head

# If migration conflicts, check versions
ls apps/api/alembic/versions/
```

## ✅ Success Criteria

Phase 6 SSE streaming is working correctly if:

- [ ] Unit tests pass (3/3)
- [ ] Integration test completes without errors
- [ ] SSE stream delivers events in real-time
- [ ] Multiple providers query concurrently
- [ ] Progress updates correctly (0% → 100%)
- [ ] Provider failures don't block other providers
- [ ] Responses and citations saved to database
- [ ] Mock mode works without API keys
- [ ] ENABLED_PROVIDERS configuration respected

## 📊 Performance Benchmarks

Expected performance:

- **Serial queries** (no concurrency): ~30s per provider × N providers
- **Concurrent queries** (Phase 6): ~30s total regardless of provider count
- **SSE latency**: < 100ms per event
- **Database writes**: < 50ms per response

Example with 2 providers and 2 prompts:
- Total queries: 4 (2 × 2)
- Expected duration: ~30-35s (concurrent)
- Without concurrency: ~120-140s

## 🔄 Next Steps

Once Phase 6 tests pass:

1. **Add remaining provider adapters:**
   - Gemini (with grounding)
   - Perplexity (native citations)
   - Google AI Search
   - Hugging Face

2. **Implement frontend SSE client:**
   - EventSource connection
   - Real-time progress UI
   - Provider status cards

3. **Add contract tests:**
   - SSE endpoint validation
   - Event format verification
   - Error handling tests

4. **Move to Phase 7:**
   - Response exploration
   - Citation review UI
   - Confidence level calculation
