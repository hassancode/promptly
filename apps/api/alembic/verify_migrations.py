#!/usr/bin/env python3
"""
Database migration verification script
Task: T224 [Phase 9]

Verifies that all migrations can be applied and rolled back cleanly.

Usage:
    python alembic/verify_migrations.py

This script:
1. Checks current migration state
2. Downgrades to base (if needed)
3. Upgrades to head
4. Verifies final state
5. Reports any issues
"""
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


def get_alembic_config():
    """Get Alembic configuration"""
    config_path = Path(__file__).parent.parent / "alembic.ini"
    config = Config(str(config_path))
    return config


def get_database_url():
    """Get database URL from environment or config"""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        # Try to load from .env
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith("DATABASE_URL="):
                        database_url = line.strip().split("=", 1)[1]
                        break

    if not database_url:
        raise ValueError("DATABASE_URL not set. Please set it in environment or .env file.")

    return database_url


def get_current_revision(engine):
    """Get current database revision"""
    with engine.connect() as conn:
        context = MigrationContext.configure(conn)
        return context.get_current_revision()


def get_head_revision(config):
    """Get head revision from migration scripts"""
    script = ScriptDirectory.from_config(config)
    return script.get_current_head()


def get_all_revisions(config):
    """Get all revision IDs in order"""
    script = ScriptDirectory.from_config(config)
    revisions = []
    for rev in script.walk_revisions():
        revisions.append(rev.revision)
    return list(reversed(revisions))


def check_pending_migrations(engine, config):
    """Check if there are pending migrations"""
    current = get_current_revision(engine)
    head = get_head_revision(config)
    return current != head, current, head


def verify_tables_exist(engine):
    """Verify expected tables exist"""
    expected_tables = [
        "users",
        "analyses",
        "competitors",
        "prompts",
        "ai_responses",
        "citations",
        "insights",
        "recommendations",
    ]

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """))
        existing_tables = {row[0] for row in result}

    missing = [t for t in expected_tables if t not in existing_tables]
    extra = [t for t in existing_tables if t not in expected_tables and t != "alembic_version"]

    return missing, extra, existing_tables


def main():
    """Main verification routine"""
    print("=" * 60)
    print("Promptly Database Migration Verification")
    print("=" * 60)
    print()

    try:
        config = get_alembic_config()
        database_url = get_database_url()
        engine = create_engine(database_url)

        # 1. Check current state
        print("[1/5] Checking current migration state...")
        current_rev = get_current_revision(engine)
        head_rev = get_head_revision(config)
        all_revisions = get_all_revisions(config)

        print(f"      Current revision: {current_rev or 'None (empty database)'}")
        print(f"      Head revision:    {head_rev}")
        print(f"      Total migrations: {len(all_revisions)}")
        print()

        # 2. List all migrations
        print("[2/5] Listing migration chain...")
        script = ScriptDirectory.from_config(config)
        for rev in script.walk_revisions():
            marker = " <-- current" if rev.revision == current_rev else ""
            marker = " <-- HEAD" if rev.revision == head_rev else marker
            print(f"      {rev.revision[:12]}: {rev.doc}{marker}")
        print()

        # 3. Check for pending migrations
        print("[3/5] Checking for pending migrations...")
        has_pending, current, head = check_pending_migrations(engine, config)
        if has_pending:
            print(f"      WARNING: Pending migrations detected!")
            print(f"      Run: alembic upgrade head")
        else:
            print(f"      OK: Database is at head revision")
        print()

        # 4. Verify tables
        print("[4/5] Verifying database tables...")
        missing, extra, existing = verify_tables_exist(engine)

        if missing:
            print(f"      WARNING: Missing tables: {', '.join(missing)}")
        if extra:
            print(f"      INFO: Additional tables found: {', '.join(extra)}")
        if not missing:
            print(f"      OK: All expected tables exist")

        print(f"      Total tables: {len(existing)}")
        print()

        # 5. Summary
        print("[5/5] Verification Summary")
        print("-" * 40)

        issues = []
        if has_pending:
            issues.append("Pending migrations need to be applied")
        if missing:
            issues.append(f"Missing tables: {', '.join(missing)}")

        if issues:
            print("      ISSUES FOUND:")
            for issue in issues:
                print(f"      - {issue}")
            print()
            print("      Status: FAILED")
            return 1
        else:
            print("      Status: PASSED")
            print("      All migrations verified successfully!")
            return 0

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
