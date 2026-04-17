#!/bin/bash

# D1 마이그레이션 실행 스크립트
# 사용: ./scripts/run-migration.sh

set -e

# 환경변수 확인
if [ -z "$CF_ACCOUNT_ID" ] || [ -z "$CF_D1_DATABASE_ID" ] || [ -z "$CF_API_TOKEN" ]; then
  echo "Error: Missing Cloudflare credentials"
  echo "Please set CF_ACCOUNT_ID, CF_D1_DATABASE_ID, CF_API_TOKEN"
  exit 1
fi

BASE_URL="https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/d1/database/$CF_D1_DATABASE_ID/query"

echo "Running D1 Migration: Add Google OAuth columns"
echo "Base URL: $BASE_URL"

# 1. google_id 컬럼 추가
echo "Adding google_id column..."
curl -X POST \
  "$BASE_URL" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sql": "ALTER TABLE users ADD COLUMN google_id TEXT UNIQUE"}' \
  -w "\nStatus: %{http_code}\n"

# 2. avatar_url 컬럼 추가
echo ""
echo "Adding avatar_url column..."
curl -X POST \
  "$BASE_URL" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sql": "ALTER TABLE users ADD COLUMN avatar_url TEXT"}' \
  -w "\nStatus: %{http_code}\n"

echo ""
echo "Migration completed!"
