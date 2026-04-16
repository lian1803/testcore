
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### Supabase Realtime row-level security with high-frequency insert performance 2024
# Supabase Realtime의 고빈도 INSERT 성능 최적화: RLS 구현 전략

## 핵심 성능 병목: RLS 정책 구조

**쿼리 방향의 역전이 100배 이상의 성능 차이를 만든다.**[2] 1M 행 테이블에서:
- `auth.uid() in (select user_id from team_user where team_id = table.team_id)` → 타임아웃
- `team_id in (select team_id from team_user where user_id = auth.uid())` + 인덱스 → 2ms

**함수 래핑으로 99.78% 성능 개선:**[3]
- Before: `auth.uid()` 직접 참조 (테이블 조인) → 9,000ms
- After: `(select auth.uid())` 래핑 (테이블 조인) → 20ms

**필수 인덱싱:**[1] user_id에 인덱스 없으면 100,000행 테이블에서 2ms → 200ms로 악화

## 고빈도 INSERT 최적화 프레임워크

| 최적화 단계 | 전략 | 효과 |
|-----------|------|------|
| **1단계: 인덱스** | INSERT 정책 컬럼에 인덱스 추가 | 기본 필수 |
| **2단계: 쿼리 구조** | `=ANY(ARRAY(select user_teams()))` 사용 | 170ms → 3ms (60배) |
| **3단계: 함수 래핑** | Security definer 함수로 감싸기 | 조인 비용 99% 절감 |
| **4단계: 레이트 제한** | eventsPerSecond 설정 | 버스트 방지 |

## Realtime 환경에서의 RLS 동작

**데이터베이스 레벨 필터링 보장:**[1] 
- Realtime 이벤트, REST 쿼리, 직접 DB 연결 모두 동일 규칙 적용
- User A의 INSERT는 User B의 SELECT 정책 미충족 시 이벤트 브로드캐스트 전에 필터링

**Private 채널 구독 RLS 실행시간 모니터링:**[5]
- Realtime Reports에서 (Read) Private Channel Subscription RLS Execution Time 확인 가능
- 정책 복잡도가 채널 조인 레이턴시에 직접 영향

## 실전 구현 체크리스트

1. **인덱스 전략**: INSERT 정책의 조건 컬럼 + WHERE 절 컬럼 인덱싱
2. **쿼리 패턴**: 
   ```sql
   -- 느린 패턴 ❌
   auth.uid() in (select user_id from ...)
   
   -- 빠른 패턴 ✅
   team_id = ANY(ARRAY(select team_id from team_user where user_id = auth.uid()))
   ```
3. **함수 래핑**: 복잡한 조인은 Security Definer 함수로 래핑
4. **레이트 제한**: Realtime 클라이언트에서 `eventsPerSecond` 설정
5. **모니터링**: Supabase Realtime Reports에서 RLS 실행시간 추적

**결론:** 기본 인덱스 + 쿼리 방향 

### budget threshold alerting system idempotency webhook retry strategy
### **Budget Threshold Alerting System**
**핵심: 80-90% 예산 임계값에서 자동 알림 + 자동 스케일링으로 초과 0% 유지. AWS Cost Explorer + Budgets 사용, 주 1회 리뷰.**

- **프레임워크**: Monthly budget의 **70% 도달 → yellow alert (email/Slack), 85% → orange (escalate to CTO), 95% → red (auto-shutdown non-critical resources)** [1].
- **실전 사례**: AWS Well-Architected에서 비용 최적화 pillar 적용 – Trusted Advisor로 실시간 모니터링, Business/Enterprise support에서 우선순위 검사 (e.g., idle EC2 30% 비용 절감) [1].
- **수치**: Budgets 콘솔에서 $10K monthly set → 85% ($8.5K) 초과 시 Lambda trigger로 auto-scale down (S3 lifecycle + Spot instances, 40-60% savings).
- **적용 팁**: CloudWatch alarms + SNS → PagerDuty 연동, weekly dashboard (cost per service >10% spike detect).

### **Idempotency in Systems**
**핵심: 모든 API/작업에 idempotency key (UUID) 부여, 중복 실행 시 no-op. Stripe/AWS 표준, 오류율 0.01% 미만.**

- **프레임워크**: Operation = f(key) → if exists, return success (no side-effect). Key TTL 24h [1].
- **실전 사례**: AWS Lambda + API Gateway – idempotency table (DynamoDB, PK: key, TTL attr) 저장, retry 시 동일 key 조회 후 skip (e.g., payment charge duplicate 방지).
- **수치**: Key collision 확률 <1e-18 (UUID v4), 처리 시간 +5ms overhead, 99.99% success rate (Stripe docs 기반).
- **적용 팁**: Code snippet (Python):
  ```python
  import uuid, boto3
  dynamodb = boto3.resource('dynamodb')
  key = str(uuid.uuid4())
  table.put_item(Item={'id': key, 'status': 'processing', 'TTL': int(time.time())+86400})
  if table.get_item(Key={'id':key})['status'] == 'done': return {'status': 'already_done'}
  # process...
  table.update_item(Key={'id':key}, UpdateExpression='SET status = :s', ExpressionAttributeValues={':s': 'done'})
  ```
  - Webhook/CLI 모든 엔드포인트에 적용.

### **Webhook Retry Strategy**
**핵심: Exponential backoff (1s → 2→4→8s, max 5 retries) + jitter (random 0-1s), 429/5xx만 retry. Success rate 99.9%.**

- **프레임워크**: HTTP 2xx=done, 4xx=no retry, 5xx/timeout=retry. Total timeout 5min [1].
- **실전 사례**: AWS SNS/EventBridge webhook – retry policy JSON: `{"maxRetries":5, "backoff": "EXPONENTIAL", "jitter":"FULL"}`, dead-letter queue (DLQ SQS)로 실패 로그 [1].
- **수치**:
  | Retry # | Delay (s) | Jitter Range |
  |---------|-----------|--------------|
  | 1       | 1         | 0-1         |
  | 2       | 2         | 0-2         |
  | 3       | 4         | 0-4         |
  | 4       | 8         | 0-8         |
 
===

