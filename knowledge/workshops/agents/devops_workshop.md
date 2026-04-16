## ── 세계 최고 DevOps 워크샵 — 10년차 인프라 마스터클래스 ──

### 🚀 Vercel 프로덕션 배포 마스터

#### 브랜치 → 환경 매핑 전략
```
feature/* → Preview 배포 (자동, PR 단위)
staging   → Staging 환경 (커스텀 도메인: staging.yourapp.com)
main      → Production (yourapp.com)
```

#### Vercel 환경 설정 (대시보드 기준)
- **Preview**: feature 브랜치마다 독립 URL 자동 생성 (`*.vercel.app`)
- **Staging**: `staging` 브랜치에 별도 도메인 연결 → QA 팀 테스트 공간
- **Production**: `main` 머지 시만 배포 → 절대 직접 푸시 금지

#### 빌드 최적화
```json
// next.config.js
module.exports = {
  output: 'standalone',           // Docker 이미지 최소화
  compress: true,                 // gzip 압축
  poweredByHeader: false,         // 보안: X-Powered-By 헤더 제거
  images: {
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 60,
  },
  experimental: {
    turbo: {},                    // Turbopack — 빌드 최대 53% 단축
  }
}
```

#### 롤백 전략 (3단계)
```bash
# 1. Vercel 대시보드에서 이전 배포 클릭 → "Promote to Production"
# 2. CLI로 즉시 롤백
vercel rollback [deployment-url] --scope=your-team

# 3. Git revert (코드베이스도 함께)
git revert HEAD --no-edit
git push origin main
```

#### Staged Production 배포 (배포 후 검증 → 전환)
```bash
# vercel.json — 자동 promote 비활성화
{
  "github": {
    "autoJobCancelation": false
  }
}
# → Vercel 대시보드에서 수동으로 "Assign to Domain" 클릭
```

---

### 🔄 CI/CD 파이프라인 설계

#### GitHub Actions 완전 자동화 워크플로우

**.github/workflows/ci.yml** — PR/feature 브랜치용 (검증)
```yaml
name: CI

on:
  pull_request:
    branches: [main, staging]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'             # node_modules 캐시 — 빌드 수분 단축

      - name: Install dependencies
        run: npm ci                # npm install 대신 ci 사용 (lockfile 엄격 준수)

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run type-check    # tsc --noEmit

      - name: Unit tests
        run: npm run test -- --coverage

      - name: Build check
        run: npm run build
        env:
          NEXT_PUBLIC_APP_URL: ${{ secrets.STAGING_URL }}
```

**.github/workflows/deploy-staging.yml** — staging 브랜치 자동 배포
```yaml
name: Deploy to Staging

on:
  push:
    branches: [staging]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Vercel Staging
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--target preview'
          alias-domains: staging.yourapp.com
```

**.github/workflows/deploy-production.yml** — main 머지 시 프로덕션 배포
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production        # GitHub Environment Protection Rules 적용
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install & Build
        run: npm ci && npm run build

      - name: Deploy to Vercel Production
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'

      - name: Notify deployment
        if: success()
        run: |
          curl -X POST ${{ secrets.DISCORD_WEBHOOK_URL }} \
            -H "Content-Type: application/json" \
            -d '{"content": "✅ Production 배포 완료: ${{ github.sha }}"}'
```

---

### 🔐 시크릿/환경변수 관리

#### 절대 원칙
```
.env          → Git 커밋 금지 (비공개 기본값, 개발자 참고용만)
.env.local    → Git 커밋 절대 금지 (실제 로컬 키)
.env.example  → Git 커밋 필수 (키 이름만, 값 없음)
```

**.gitignore** 필수 항목
```gitignore
.env
.env.local
.env.*.local
.env.production
```

#### Next.js 변수 규칙
```bash
# 서버 전용 (Node.js만 접근 — 절대 브라우저 노출 안됨)
DATABASE_URL=postgres://...
STRIPE_SECRET_KEY=sk_live_...
ANTHROPIC_API_KEY=sk-ant-...

# 클라이언트 노출 가능 (NEXT_PUBLIC_ 접두사)
NEXT_PUBLIC_APP_URL=https://yourapp.com
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

#### Vercel 환경별 변수 분리
```bash
# Vercel CLI로 환경변수 설정
vercel env add DATABASE_URL production     # 프로덕션만
vercel env add DATABASE_URL preview        # 스테이징/프리뷰
vercel env add DATABASE_URL development    # 로컬 개발

# 로컬에 프리뷰 변수 다운로드
vercel env pull .env.local

# 현재 설정된 변수 확인
vercel env ls
```

#### 서버 전용 보호 (Next.js 15+)
```typescript
// lib/data-access.ts — 클라이언트에서 임포트 시 빌드 에러 발생
import 'server-only'

export async function getSecretData() {
  // DB 직접 쿼리 — 브라우저에서 절대 실행 불가
}
```

---

### 📊 모니터링 & 알림 설정

#### 최소 비용 최대 가시성 스택 (무료 ~ 월 $26)

| 도구 | 용도 | 비용 |
|------|------|------|
| Vercel Analytics | 웹 성능 (Core Web Vitals) | 무료 |
| Vercel Speed Insights | 실제 사용자 성능 측정 | 무료 |
| Sentry (Free) | 에러 추적 + 스택 트레이스 | 무료 (5K events/월) |
| BetterStack (Uptime) | 업타임 모니터링 + 알림 | 무료 |

#### Sentry 설치 (Next.js)
```bash
npx @sentry/wizard@latest -i nextjs
```

자동 생성 파일:
```
sentry.client.config.ts   ← 클라이언트 에러 캐치
sentry.server.config.ts   ← 서버/API 에러 캐치
sentry.edge.config.ts     ← Edge Runtime 에러 캐치
next.config.js            ← withSentryConfig 래핑
```

**sentry.client.config.ts** 핵심 설정
```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,          // 프로덕션: 10% 샘플링 (비용 절감)
  replaysOnErrorSampleRate: 1.0,  // 에러 발생 시 100% 세션 리플레이
  replaysSessionSampleRate: 0.01, // 일반 세션: 1% 샘플링
  environment: process.env.NODE_ENV,
  beforeSend(event) {
    // 민감 정보 필터링
    if (event.request?.headers) {
      delete event.request.headers['Authorization'];
    }
    return event;
  },
});
```

#### Vercel 로그 드레인 → Sentry 연동
```
Vercel 대시보드 → Project → Settings → Log Drains
→ Sentry Endpoint 추가 → 모든 로그 자동 포워딩
```

#### 에러 알림 Discord 연동 (Sentry)
```
Sentry → Settings → Integrations → Webhooks
→ Discord Webhook URL 입력
→ 알림 조건: 새 이슈 발생, 에러율 급증 (1분 내 10건+)
```

---

### 🗄️ DB 마이그레이션 무중단 전략

#### Prisma 프로덕션 마이그레이션 플로우
```bash
# 1. 마이그레이션 파일 생성 (로컬)
npx prisma migrate dev --name add_user_avatar

# 2. 프로덕션 적용 (다운타임 없는 명령어)
npx prisma migrate deploy    # reset 절대 금지! deploy만 사용
```

#### Expand and Contract 패턴 (컬럼 변경 시)

**Phase 1 — Expand (새 컬럼 추가, 기존 유지)**
```prisma
// schema.prisma
model User {
  id        String  @id
  name      String  // 기존 (유지)
  firstName String? // 신규 추가 (nullable로!)
  lastName  String? // 신규 추가 (nullable로!)
}
```
```bash
npx prisma migrate deploy  # 배포 — 다운타임 없음
```

**Phase 2 — Migrate (데이터 이전)**
```typescript
// 백그라운드 스크립트로 조금씩 이전
const users = await prisma.user.findMany({ where: { firstName: null } });
for (const user of users) {
  const [first, ...rest] = user.name.split(' ');
  await prisma.user.update({
    where: { id: user.id },
    data: { firstName: first, lastName: rest.join(' ') }
  });
}
```

**Phase 3 — Contract (기존 컬럼 제거)**
```prisma
// 모든 코드가 firstName/lastName 사용 확인 후
model User {
  id        String @id
  // name 삭제
  firstName String
  lastName  String
}
```
```bash
npx prisma migrate deploy  # 기존 name 컬럼 DROP
```

#### 위험한 마이그레이션 체크리스트
```bash
# 마이그레이션 전 반드시 확인
npx prisma migrate diff \
  --from-schema-datamodel prisma/schema.prisma \
  --to-migrations prisma/migrations \
  --script

# 결과에서 이것들 보이면 위험 신호:
# DROP COLUMN   → 데이터 손실
# NOT NULL      → 기존 레코드 에러
# RENAME TABLE  → 외래키 깨짐
```

#### GitHub Actions에 마이그레이션 자동화
```yaml
- name: Run DB migrations
  run: npx prisma migrate deploy
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  # deploy 전 실행 — 코드와 DB 스키마 항상 동기화
```

---

### 📦 패키지 보안 관리

#### 일상 보안 루틴
```bash
# 취약점 전체 스캔
npm audit

# 자동 수정 (안전한 버전으로만)
npm audit fix

# 강제 수정 (breaking change 포함 — 주의!)
npm audit fix --force

# JSON 출력 (CI 파이프라인 통합용)
npm audit --json | jq '.vulnerabilities | keys[]'
```

#### 취약점 우선순위
```
critical  → 즉시 수정 (24시간 이내)
high      → 이번 스프린트 내 수정
moderate  → 다음 스프린트
low       → 분기별 정리
```

#### Dependabot 설정 (**.github/dependabot.yml**)
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"         # 매주 월요일
      day: "monday"
      time: "09:00"
      timezone: "Asia/Seoul"
    target-branch: "staging"     # main 직접 PR 금지
    open-pull-requests-limit: 5  # PR 폭탄 방지
    groups:
      dev-dependencies:          # 개발 의존성 묶어서 PR 1개로
        dependency-type: "development"
    ignore:
      - dependency-name: "*"
        update-types: ["version-update:semver-major"]  # major 업데이트 수동 처리
```

#### 패키지 설치 전 보안 체크 (2025 공급망 공격 대응)
```bash
# 설치 전 해당 패키지 평판 확인
npm info [패키지명] | grep -E 'version|maintainers|downloads'

# 라이프사이클 스크립트 비활성화 (postinstall 악성 스크립트 방지)
npm install --ignore-scripts [패키지명]

# package-lock.json 무결성 검증
npm ci --audit                   # CI 환경: lockfile 엄격 준수 + 자동 audit

# .npmrc에 보안 설정 고정
echo "ignore-scripts=false" > .npmrc   # 신뢰하는 패키지만 scripts 허용
echo "audit=true" >> .npmrc
```

#### 버전 고정 전략
```json
// package.json — ^ 대신 정확한 버전 고정 (프로덕션)
{
  "dependencies": {
    "next": "15.1.0",           // ^ 없음 — 예측 가능한 빌드
    "react": "19.0.0",
    "prisma": "6.2.1"
  },
  "devDependencies": {
    "typescript": "^5.7.0"     // devDep은 ^ 허용 (빌드만 영향)
  }
}
```

```bash
# 전체 의존성 최신 버전 확인 (업그레이드 검토용)
npx npm-check-updates

# 안전한 것만 자동 업그레이드
npx npm-check-updates -u --target minor
npm install
npm test  # 테스트 통과하면 커밋
```
