#!/bin/bash
set -e

echo "Setting up Promptly development environment..."

# Install Poetry
echo "Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"

# Setup Backend
echo "Setting up backend..."
cd /workspace/apps/api

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    # Update with container-friendly values
    sed -i 's|DATABASE_URL=.*|DATABASE_URL=postgresql://promptly:promptly_dev@db:5432/promptly|' .env
    sed -i 's|REDIS_URL=.*|REDIS_URL=redis://redis:6379|' .env
    sed -i 's|SECRET_KEY=.*|SECRET_KEY=dev_secret_key_change_in_production_12345|' .env
fi

# Install Python dependencies
poetry install

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
for i in {1..30}; do
    if poetry run python -c "from sqlalchemy import create_engine; e = create_engine('postgresql://promptly:promptly_dev@db:5432/promptly'); e.connect()" 2>/dev/null; then
        echo "PostgreSQL is ready!"
        break
    fi
    echo "Waiting for PostgreSQL... ($i/30)"
    sleep 2
done

# Run migrations
echo "Running database migrations..."
poetry run alembic upgrade head

# Setup Frontend
echo "Setting up frontend..."
cd /workspace/apps/web

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

# Install Node dependencies
npm install

echo ""
echo "========================================="
echo "Setup complete!"
echo ""
echo "To start the backend:"
echo "  cd /workspace/apps/api"
echo "  poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "To start the frontend (new terminal):"
echo "  cd /workspace/apps/web"
echo "  npm run dev"
echo ""
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo "========================================="
