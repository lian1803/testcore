#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick test for benchmark builder setup"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent / "team" / "[진행중] 오프라인 마케팅" / "소상공인_영업툴" / "naver-diagnosis"
sys.path.insert(0, str(PROJECT_ROOT))

print("[IMPORT CHECK]")
try:
    from models import BenchmarkPremium
    print("[OK] BenchmarkPremium imported")
except Exception as e:
    print(f"[FAIL] BenchmarkPremium: {e}")
    sys.exit(1)

try:
    from database import Base, init_db
    print("[OK] database module imported")
except Exception as e:
    print(f"[FAIL] database: {e}")
    sys.exit(1)

try:
    from services.benchmark_builder import BenchmarkBuilder
    print("[OK] BenchmarkBuilder imported")
except Exception as e:
    print(f"[FAIL] BenchmarkBuilder: {e}")
    sys.exit(1)

try:
    from services.concept_analyzer import ConceptAnalyzer
    print("[OK] ConceptAnalyzer imported")
except Exception as e:
    print(f"[FAIL] ConceptAnalyzer: {e}")
    sys.exit(1)

print()
print("[DB SCHEMA CHECK]")
from sqlalchemy import inspect

mapper = inspect(BenchmarkPremium)
print(f"Table: {BenchmarkPremium.__tablename__}")
print(f"Columns: {len(mapper.columns)}")
print("Sample columns:")
for col in list(mapper.columns)[:8]:
    print(f"  - {col.name}: {col.type}")

print()
print("[QUERY GENERATION CHECK]")
import asyncio

async def test_queries():
    builder = BenchmarkBuilder()
    queries = await builder.generate_queries()
    print(f"Generated queries: {len(queries)}")
    for q in queries[:3]:
        print(f"  - {q['query']} (category={q['category']}, region={q['region']})")
    await builder.close()

asyncio.run(test_queries())

print()
print("[ALL CHECKS PASSED]")
