#!/usr/bin/env python3
"""
D1 마이그레이션 실행 스크립트 (크로스 플랫폼)
사용: python scripts/run-migration.py
"""

import os
import sys
import requests
import json

def run_migration():
    # 환경변수 확인
    cf_account_id = os.getenv('CF_ACCOUNT_ID')
    cf_d1_database_id = os.getenv('CF_D1_DATABASE_ID')
    cf_api_token = os.getenv('CF_API_TOKEN')

    if not all([cf_account_id, cf_d1_database_id, cf_api_token]):
        print("Error: Missing Cloudflare credentials")
        print("Please set CF_ACCOUNT_ID, CF_D1_DATABASE_ID, CF_API_TOKEN")
        return False

    base_url = f"https://api.cloudflare.com/client/v4/accounts/{cf_account_id}/d1/database/{cf_d1_database_id}/query"
    headers = {
        'Authorization': f'Bearer {cf_api_token}',
        'Content-Type': 'application/json',
    }

    print("Running D1 Migration: Add Google OAuth columns")
    print(f"Base URL: {base_url}")
    print()

    # 마이그레이션 SQL 쿼리들
    migrations = [
        ("Adding google_id column...", "ALTER TABLE users ADD COLUMN google_id TEXT UNIQUE"),
        ("Adding avatar_url column...", "ALTER TABLE users ADD COLUMN avatar_url TEXT"),
    ]

    for step_name, sql in migrations:
        print(step_name)
        try:
            response = requests.post(
                base_url,
                headers=headers,
                json={'sql': sql},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✓ Success: {result}")
                else:
                    print(f"✗ Failed: {result}")
                    return False
            else:
                print(f"✗ HTTP {response.status_code}: {response.text}")
                # 컬럼이 이미 존재하는 경우는 무시
                if "already exists" in response.text or "duplicate column" in response.text.lower():
                    print("  (Column already exists - skipping)")
                else:
                    return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
        print()

    print("Migration completed!")
    return True

if __name__ == '__main__':
    try:
        success = run_migration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nMigration cancelled")
        sys.exit(1)
