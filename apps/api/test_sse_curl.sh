#!/bin/bash
# Test SSE Streaming Endpoint
#
# Prerequisites:
# 1. Database running (PostgreSQL)
# 2. Redis running
# 3. API server running on port 8000
# 4. User account created and session cookie obtained

set -e

API_BASE="http://localhost:8000/api/v1"
COOKIE_FILE="test_session.txt"

echo "========================================="
echo "SSE Streaming Endpoint Test"
echo "========================================="
echo ""

# Function to check if API is running
check_api() {
    echo "📡 Checking if API is running..."
    if curl -s "$API_BASE/ping" > /dev/null 2>&1; then
        echo "   ✓ API is running"
        return 0
    else
        echo "   ✗ API is not running"
        echo "   Please start the API server:"
        echo "   cd apps/api && poetry run uvicorn src.main:app --reload"
        return 1
    fi
}

# Function to register and login
setup_test_user() {
    echo ""
    echo "👤 Setting up test user..."

    # Generate random email
    TEST_EMAIL="sse-test-$(date +%s)@example.com"
    TEST_PASSWORD="SecurePass123!"

    echo "   Email: $TEST_EMAIL"

    # Register
    echo "   Registering..."
    REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

    if echo "$REGISTER_RESPONSE" | grep -q "id"; then
        echo "   ✓ Registration successful"
    else
        echo "   ✗ Registration failed: $REGISTER_RESPONSE"
        return 1
    fi

    # Login and save cookie
    echo "   Logging in..."
    LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" \
        -c "$COOKIE_FILE")

    if echo "$LOGIN_RESPONSE" | grep -q "id"; then
        echo "   ✓ Login successful"
        echo "   Cookie saved to: $COOKIE_FILE"
        return 0
    else
        echo "   ✗ Login failed: $LOGIN_RESPONSE"
        return 1
    fi
}

# Function to create analysis
create_analysis() {
    echo ""
    echo "📊 Creating test analysis..."

    ANALYSIS_RESPONSE=$(curl -s -X POST "$API_BASE/analyses" \
        -H "Content-Type: application/json" \
        -b "$COOKIE_FILE" \
        -d '{"brand_name":"Tesla"}')

    ANALYSIS_ID=$(echo "$ANALYSIS_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

    if [ -z "$ANALYSIS_ID" ]; then
        echo "   ✗ Failed to create analysis: $ANALYSIS_RESPONSE"
        return 1
    fi

    echo "   ✓ Analysis created: $ANALYSIS_ID"
    echo "$ANALYSIS_ID"
}

# Function to add competitors
add_competitors() {
    local ANALYSIS_ID=$1
    echo ""
    echo "🏁 Adding competitors..."

    for competitor in "Rivian" "Lucid Motors"; do
        RESPONSE=$(curl -s -X POST "$API_BASE/analyses/$ANALYSIS_ID/competitors" \
            -H "Content-Type: application/json" \
            -b "$COOKIE_FILE" \
            -d "{\"competitor_name\":\"$competitor\"}")

        if echo "$RESPONSE" | grep -q "id"; then
            echo "   ✓ Added: $competitor"
        else
            echo "   ✗ Failed to add $competitor"
        fi
    done
}

# Function to add prompts
add_prompts() {
    local ANALYSIS_ID=$1
    echo ""
    echo "❓ Adding prompts..."

    PROMPTS=(
        "What are the best electric vehicles for long-distance travel?"
        "Which EV manufacturer has the best charging infrastructure?"
    )

    for prompt in "${PROMPTS[@]}"; do
        RESPONSE=$(curl -s -X POST "$API_BASE/analyses/$ANALYSIS_ID/prompts" \
            -H "Content-Type: application/json" \
            -b "$COOKIE_FILE" \
            -d "{\"prompt_text\":\"$prompt\"}")

        if echo "$RESPONSE" | grep -q "id"; then
            echo "   ✓ Added prompt"
        else
            echo "   ✗ Failed to add prompt"
        fi
    done
}

# Function to test SSE streaming
test_sse_stream() {
    local ANALYSIS_ID=$1
    echo ""
    echo "========================================="
    echo "🔴 TESTING SSE STREAMING"
    echo "========================================="
    echo ""
    echo "Analysis ID: $ANALYSIS_ID"
    echo "Endpoint: $API_BASE/analyses/$ANALYSIS_ID/stream"
    echo ""
    echo "Connecting to SSE stream..."
    echo "Press Ctrl+C to stop"
    echo ""

    # Stream SSE events
    curl -N -b "$COOKIE_FILE" \
        "$API_BASE/analyses/$ANALYSIS_ID/stream" \
        2>&1 | while IFS= read -r line; do

        # Parse SSE events
        if [[ $line == event:* ]]; then
            EVENT_TYPE=$(echo "$line" | cut -d' ' -f2-)
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "📡 Event: $EVENT_TYPE"
        elif [[ $line == data:* ]]; then
            DATA=$(echo "$line" | cut -d' ' -f2-)
            echo "📦 Data: $DATA" | python3 -m json.tool 2>/dev/null || echo "$DATA"
        fi
    done
}

# Main execution
main() {
    # Check API
    if ! check_api; then
        exit 1
    fi

    # Setup test user
    if ! setup_test_user; then
        exit 1
    fi

    # Create analysis
    ANALYSIS_ID=$(create_analysis)
    if [ -z "$ANALYSIS_ID" ]; then
        exit 1
    fi

    # Add competitors
    add_competitors "$ANALYSIS_ID"

    # Add prompts
    add_prompts "$ANALYSIS_ID"

    # Test SSE stream
    test_sse_stream "$ANALYSIS_ID"
}

# Cleanup function
cleanup() {
    echo ""
    echo ""
    echo "🧹 Cleaning up..."
    rm -f "$COOKIE_FILE"
    echo "   ✓ Cleanup complete"
}

trap cleanup EXIT

# Run main
main
