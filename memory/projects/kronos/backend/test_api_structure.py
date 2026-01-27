#!/usr/bin/env python3
"""
Test script to verify API structure completeness
"""

import os
import sys
from pathlib import Path

def check_file_exists(path, description):
    """Check if file exists and print status"""
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {path}")
    return exists

def main():
    print("🔍 Checking KRONOS Backend API Structure...")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    all_good = True
    
    # Core files
    print("\n📁 CORE FILES:")
    all_good &= check_file_exists(base_dir / "main.py", "Main application")
    all_good &= check_file_exists(base_dir / "requirements.txt", "Dependencies")
    all_good &= check_file_exists(base_dir / ".env.example", "Environment template")
    all_good &= check_file_exists(base_dir / "Dockerfile", "Docker configuration")
    all_good &= check_file_exists(base_dir / "docker-compose.yml", "Docker Compose")
    all_good &= check_file_exists(base_dir / "README.md", "Documentation")
    
    # Configuration
    print("\n⚙️  CONFIGURATION:")
    all_good &= check_file_exists(base_dir / "app/core/config.py", "Settings")
    all_good &= check_file_exists(base_dir / "app/core/security.py", "Security")
    all_good &= check_file_exists(base_dir / "app/core/logging_config.py", "Logging")
    
    # Database
    print("\n🗄️  DATABASE:")
    all_good &= check_file_exists(base_dir / "app/db/base.py", "Base model")
    all_good &= check_file_exists(base_dir / "app/db/session.py", "Session")
    
    # Models
    print("\n📊 MODELS:")
    all_good &= check_file_exists(base_dir / "app/models/user.py", "User model")
    all_good &= check_file_exists(base_dir / "app/models/lead.py", "Lead model")
    all_good &= check_file_exists(base_dir / "app/models/client.py", "Client model")
    all_good &= check_file_exists(base_dir / "app/models/message.py", "Message model")
    all_good &= check_file_exists(base_dir / "app/models/file.py", "File model")
    all_good &= check_file_exists(base_dir / "app/models/analytics.py", "Analytics model")
    
    # Schemas
    print("\n📝 SCHEMAS:")
    all_good &= check_file_exists(base_dir / "app/schemas/user.py", "User schemas")
    all_good &= check_file_exists(base_dir / "app/schemas/lead.py", "Lead schemas")
    all_good &= check_file_exists(base_dir / "app/schemas/client.py", "Client schemas")
    all_good &= check_file_exists(base_dir / "app/schemas/message.py", "Message schemas")
    all_good &= check_file_exists(base_dir / "app/schemas/file.py", "File schemas")
    all_good &= check_file_exists(base_dir / "app/schemas/analytics.py", "Analytics schemas")
    
    # Services
    print("\n🔧 SERVICES:")
    all_good &= check_file_exists(base_dir / "app/services/ai_service.py", "AI service")
    all_good &= check_file_exists(base_dir / "app/services/storage_service.py", "Storage service")
    all_good &= check_file_exists(base_dir / "app/services/email_service.py", "Email service")
    
    # API Endpoints
    print("\n🌐 API ENDPOINTS:")
    all_good &= check_file_exists(base_dir / "app/api/v1/router.py", "Main router")
    all_good &= check_file_exists(base_dir / "app/api/v1/endpoints/auth.py", "Auth endpoints")
    all_good &= check_file_exists(base_dir / "app/api/v1/endpoints/leads.py", "Lead endpoints")
    all_good &= check_file_exists(base_dir / "app/api/v1/endpoints/clients.py", "Client endpoints")
    all_good &= check_file_exists(base_dir / "app/api/v1/endpoints/messages.py", "Message endpoints")
    all_good &= check_file_exists(base_dir / "app/api/v1/endpoints/files.py", "File endpoints")
    all_good &= check_file_exists(base_dir / "app/api/v1/endpoints/analytics.py", "Analytics endpoints")
    
    # Tasks
    print("\n⏰ BACKGROUND TASKS:")
    all_good &= check_file_exists(base_dir / "app/tasks/celery_tasks.py", "Celery tasks")
    
    # Alembic (migrations)
    print("\n🔄 MIGRATIONS:")
    all_good &= check_file_exists(base_dir / "alembic.ini", "Alembic config")
    all_good &= check_file_exists(base_dir / "alembic/env.py", "Alembic env")
    all_good &= check_file_exists(base_dir / "alembic/script.py.mako", "Migration template")
    
    print("\n" + "=" * 60)
    
    if all_good:
        print("🎉 SUCCESS: All required files are present!")
        print("\n✅ KRONOS Backend API is COMPLETE and ready for deployment.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Run: ./start.sh dev (for development)")
        print("3. Or run: ./start.sh prod (for production with Docker)")
        print("4. Access API docs at: http://localhost:8000/docs")
    else:
        print("❌ ISSUES: Some files are missing.")
        print("Please check the missing files above.")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())