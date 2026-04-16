## ── 세계 최고 QA 워크샵 — 10년차 QA 엔지니어 마스터클래스 ──

### 테스트 피라미드 전략

**SaaS 권장 비율: Unit 70% / Integration 20% / E2E 10%**

왜 이 비율인가:
- Unit은 실행 비용 거의 0원, 버그의 70%를 잡음. CI 매 Push마다 전부 실행 가능.
- Integration은 서비스 간 계약(API 응답 스펙, DB 쿼리 결과)을 검증. 유닛이 다 통과해도 여기서 버그 발견.
- E2E는 실제 브라우저로 전체 플로우 검증. 느리고 불안정하지만 배포 전 마지막 관문.

**각 레이어가 커버하는 것:**

| 레이어 | 무엇을 테스트 | 실행 주기 | 목표 실행 시간 |
|--------|-------------|----------|--------------|
| Unit | 함수/컴포넌트 단위 로직, 순수 계산, 에러 핸들링 분기 | 모든 Push | ≤ 2~3분 |
| Integration | API 엔드포인트, DB 쿼리, 서드파티 연동, 인증 미들웨어 | PR 머지 전 | ≤ 5~7분 |
| E2E | 결제 플로우, 회원가입~로그인~핵심 기능 전체, 권한별 시나리오 | PR 머지 전 (smoke) + 야간 전체 실행 | smoke < 3분 / full 야간 |

**마이크로서비스 아키텍처면:** Integration 비중을 30%로 높여라 (서비스 간 계약 검증이 더 중요).

**실제 적용 원칙:**
- 유닛으로 커버 가능한 건 절대 E2E로 테스트하지 마라 (10배 느리고, flaky해짐)
- E2E는 "사용자가 실제로 하는 행동" 기준으로만 작성
- 테스트 하나가 깨지면 딱 하나의 이유만 있어야 함 (테스트 격리 원칙)

---

### Playwright E2E 실전 패턴

#### 1. 페이지 객체 패턴 (Page Object Model)

셀렉터가 바뀌면 한 곳만 고치면 된다. 테스트 파일에 직접 셀렉터 쓰는 건 금지.

```typescript
// pages/LoginPage.ts
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    // data-testid 우선 사용 — CSS 클래스/구조 변경에 내성
    this.emailInput = page.getByTestId('login-email');
    this.passwordInput = page.getByTestId('login-password');
    this.submitButton = page.getByRole('button', { name: '로그인' });
    this.errorMessage = page.getByTestId('login-error');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await this.errorMessage.waitFor({ state: 'visible' });
    await expect(this.errorMessage).toContainText(message);
  }
}

// tests/e2e/auth/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../../pages/LoginPage';

test.describe('로그인 플로우', () => {
  test('올바른 자격증명으로 로그인 성공', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await page.goto('/login');
    await loginPage.login('user@example.com', 'password123');
    await expect(page).toHaveURL('/dashboard');
  });

  test('잘못된 비밀번호 에러 표시', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await page.goto('/login');
    await loginPage.login('user@example.com', 'wrongpassword');
    await loginPage.expectError('이메일 또는 비밀번호가 올바르지 않습니다');
  });
});
```

#### 2. 인증 처리 (매 테스트마다 로그인 반복 금지)

```typescript
// fixtures/auth.ts — 인증 상태를 파일로 저장, 재사용
import { test as base } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    // storageState로 저장된 세션 재사용 (로그인 UI 반복 없음)
    await page.goto('/login');
    const loginPage = new LoginPage(page);
    await loginPage.login(process.env.TEST_EMAIL!, process.env.TEST_PASSWORD!);
    await page.waitForURL('/dashboard');
    await use(page);
  },
});

// playwright.config.ts — 전역 setup으로 인증 상태 저장
export default defineConfig({
  globalSetup: './global-setup.ts', // 한 번만 로그인 → auth.json 저장
  projects: [
    {
      name: 'authenticated',
      use: { storageState: 'playwright/.auth/user.json' },
    },
  ],
});
```

#### 3. API Mock (외부 의존성 제거)

```typescript
// 결제 API mock — 실제 카드 청구 없이 결제 플로우 테스트
test('결제 성공 플로우', async ({ page }) => {
  // 네트워크 요청 가로채기
  await page.route('**/api/payment/charge', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, transactionId: 'test-txn-001' }),
    });
  });

  await page.goto('/checkout');
  // ... 결제 진행
  await expect(page.getByTestId('payment-success')).toBeVisible();
});

// 결제 실패 케이스
test('카드 거절 처리', async ({ page }) => {
  await page.route('**/api/payment/charge', async route => {
    await route.fulfill({
      status: 402,
      body: JSON.stringify({ error: 'card_declined', message: '카드가 거절되었습니다' }),
    });
  });
  // ... 에러 메시지 확인
});
```

#### 4. 스크린샷 비교 (Visual Regression)

```typescript
test('대시보드 레이아웃 회귀 테스트', async ({ page }) => {
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle'); // 로딩 완료 대기
  
  // 스크린샷 비교 — 처음엔 기준 생성, 이후엔 diff 체크
  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixels: 100, // 폰트 렌더링 차이 허용
    mask: [page.getByTestId('dynamic-timestamp')], // 동적 콘텐츠 마스킹
  });
});
```

**절대 금지:**
```typescript
// X — 절대 쓰지 마라. CI에서 랜덤으로 실패함
await page.waitForTimeout(3000);

// O — 조건이 충족될 때까지 대기
await page.waitForSelector('[data-testid="results-loaded"]');
await expect(page.getByTestId('spinner')).toBeHidden();
```

**폴더 구조:**
```
tests/
  e2e/
    auth/       ← 인증 플로우
    billing/    ← 결제 플로우
    dashboard/  ← 핵심 기능
  pages/        ← Page Object 클래스
  fixtures/     ← 인증, DB 시드 등 공통 fixture
  utils/        ← 헬퍼 함수
```

---

### 리스크 기반 테스트 우선순위

**핵심 원칙: 모든 걸 다 테스트할 수 없다. 돈/데이터/신뢰를 건드리는 것부터.**

**리스크 매트릭스 (확률 × 영향도):**

| 영역 | 실패 확률 | 비즈니스 영향 | 우선순위 |
|------|----------|------------|---------|
| 결제/구독 처리 | 중 | 직접 매출 손실 | P0 — 절대 배포 전 검증 |
| 인증/권한 (로그인, RLS, 역할) | 중 | 보안 사고, 법적 리스크 | P0 |
| 데이터 쓰기 (저장, 수정, 삭제) | 중 | 데이터 손실/오염 | P0 |
| 핵심 제품 플로우 (사용자가 돈 내는 이유) | 낮 | 이탈, 환불 | P1 |
| 이메일/알림 발송 | 중 | 사용자 불편 | P1 |
| 검색/필터링 | 낮 | 불편함 | P2 |
| 대시보드 차트/통계 | 낮 | 불편함 | P2 |
| 마케팅 페이지, 정적 콘텐츠 | 매우 낮 | 이미지 손상 | P3 |

**실전 적용:**
1. P0 항목은 모든 PR에서 자동 회귀 테스트 실행
2. P1은 배포 전 smoke test
3. P2~P3는 주간 또는 야간 full run
4. 새 기능 추가 시 → 그 기능의 리스크 등급부터 판단

**파레토 법칙 적용:** 버그의 80%는 전체 코드의 20%에서 나온다. 과거 버그가 많았던 모듈부터 집중 테스트.

---

### 버그 리포트 작성법 (개발자가 바로 고칠 수 있게)

**나쁜 버그 리포트 vs 좋은 버그 리포트:**

```
# X 나쁜 예
제목: 버튼이 안 눌려요
설명: 결제 버튼 클릭하면 아무것도 안 됨

# O 좋은 예 (아래 템플릿 사용)
```

**버그 리포트 표준 템플릿:**

```markdown
## [BUG] 결제 버튼 클릭 시 로딩 스피너가 무한 회전, 에러 메시지 없음

### 심각도
- [ ] P0 — 서비스 중단/데이터 손실/보안
- [x] P1 — 핵심 기능 불가
- [ ] P2 — 기능 일부 제한
- [ ] P3 — UI/UX 불편

### 재현 단계
1. `/pricing` 페이지 접근
2. "Pro 플랜" 선택 → "결제하기" 클릭
3. 카드 번호 `4242 4242 4242 4242` 입력 (Stripe 테스트 카드)
4. "결제 완료" 버튼 클릭

### 예상 동작
결제 처리 후 `/dashboard?upgraded=true`로 이동, 성공 토스트 표시

### 실제 동작
버튼이 로딩 상태로 전환되고 약 30초 후 아무 응답 없이 버튼이 다시 활성화됨.
결제는 실제로 처리됨 (Stripe 대시보드에서 확인). 사용자에게 아무 피드백 없음.

### 환경 정보
- 브라우저: Chrome 122.0.6261.112
- OS: macOS 14.3
- 화면 크기: 1440px
- 계정: test-pro@example.com (플랜: Free)
- 재현율: 10/10 (100%)

### 로그/스크린샷
```
POST /api/payment/charge → 200 OK (응답 시간: 28.3초)
Console error: "TypeError: Cannot read properties of undefined (reading 'redirect')"
```
[스크린샷 첨부]

### 추정 원인 (QA 의견)
`payment/charge` API 성공 응답 후 `router.push()` 호출 시점에 `router` 객체가 undefined인 것으로 추정.
`useRouter` 훅 초기화 타이밍 문제 또는 응답 핸들러에서 `router` 참조 누락.
```

**작성 규칙:**
- 제목에 [어디서][무엇이][어떻게] 3가지 포함
- 재현 단계는 복사-붙여넣기해서 그대로 따라할 수 있는 수준
- "가끔", "때때로" 쓰지 마라 → 재현율 % 명시
- 스크린샷 없으면 비디오 첨부 (Loom, 화면 녹화)
- 콘솔 에러, 네트워크 탭 로그 항상 포함

---

### 릴리즈 전 체크리스트

배포 전 이 목록 전부 체크. 하나라도 FAIL이면 배포 중단.

#### 기능 검증
- [ ] 이번 릴리즈에서 변경된 모든 기능 수동 확인
- [ ] 회귀 테스트 suite 전체 PASS (자동화)
- [ ] 핵심 사용자 플로우 E2E PASS: 가입 → 로그인 → 핵심 기능 → 로그아웃
- [ ] 결제 플로우 PASS (Stripe 테스트 모드)
- [ ] 역할별 권한 확인 (Admin / User / Guest 각각)

#### 성능 검증
- [ ] Lighthouse Performance 점수 ≥ 80
- [ ] 핵심 페이지 LCP (Largest Contentful Paint) ≤ 2.5초
- [ ] API 응답 시간 P95 ≤ 500ms
- [ ] 번들 사이즈 증가 여부 확인 (이전 배포 대비 +20% 초과 시 검토)

#### 보안 검증
- [ ] 인증 우회 시도 → 401/403 정상 반환
- [ ] 다른 사용자 데이터 접근 불가 (RLS/권한 확인)
- [ ] 환경변수 노출 없음 (`.env` 파일, API 키 콘솔 출력 없음)
- [ ] HTTPS 강제 리다이렉트 동작

#### 접근성 (Accessibility)
- [ ] axe DevTools 자동 스캔 — Critical/Serious 이슈 0개
- [ ] 키보드만으로 핵심 플로우 완료 가능 (Tab → Enter 네비게이션)
- [ ] 이미지 alt 텍스트 존재
- [ ] 명도 대비 WCAG AA 기준 충족 (텍스트 4.5:1, 대형 텍스트 3:1)
- [ ] 스크린리더 (VoiceOver/NVDA) 핵심 플로우 통과

#### 모바일 반응형
- [ ] 320px (iPhone SE) — 레이아웃 깨짐 없음
- [ ] 375px (iPhone 14) — 기준 레이아웃
- [ ] 768px (iPad) — 태블릿 레이아웃
- [ ] 1440px (Desktop) — 최대 너비
- [ ] 터치 타깃 크기 ≥ 44×44px (WCAG 2.5.5)
- [ ] 가로 스크롤 없음

#### 배포 직후 확인 (5분 이내)
- [ ] 에러 모니터링 (Sentry 등) 급증 없음
- [ ] 핵심 API 에러율 정상 범위
- [ ] 신규 가입/로그인 정상 작동
- [ ] 이전 버전 롤백 플랜 준비됨

---

### 흔한 SaaS 버그 패턴

10년치 버그 데이터에서 반복적으로 나오는 패턴. 코드 리뷰 때 이것부터 체크해라.

#### 인증 Edge Case

```typescript
// 패턴 1: 토큰 만료 처리 누락
// X — 토큰 만료 시 무한 로딩 or 빈 화면
const data = await fetchWithAuth('/api/user');

// O — 401 받으면 자동 로그아웃 + 로그인 페이지 리다이렉트
const data = await fetchWithAuth('/api/user').catch(err => {
  if (err.status === 401) {
    clearAuthToken();
    router.push('/login?reason=session_expired');
  }
});
```

자주 누락되는 인증 케이스:
- 탭 여러 개 열었을 때 한 탭에서 로그아웃 → 다른 탭 동작 (로컬스토리지 이벤트 구독 필요)
- 비밀번호 재설정 링크 — 이미 사용한 링크 재사용 가능 여부
- 소셜 로그인 + 이메일 로그인 동일 이메일로 계정 충돌
- 로그인 직후 이전 페이지로 리다이렉트 (redirect_to 파라미터 처리)
- 세션 만료 중 폼 작성 완료 → 제출 → 데이터 유실

#### 결제 실패 처리

```typescript
// X — 결제 실패를 조용히 무시
const result = await stripe.confirmPayment({ elements });
if (result.paymentIntent?.status === 'succeeded') {
  router.push('/success');
}
// 실패 케이스 처리 없음 → 사용자는 왜 안 되는지 모름

// O — 실패 케이스 명시적 처리
const result = await stripe.confirmPayment({ elements });
if (result.error) {
  // Stripe 에러 코드 → 사용자 친화적 메시지로 변환
  const userMessage = {
    'card_declined': '카드가 거절되었습니다. 다른 카드를 사용해 주세요.',
    'insufficient_funds': '잔액이 부족합니다.',
    'expired_card': '카드 유효기간이 만료되었습니다.',
    'incorrect_cvc': 'CVC 번호가 올바르지 않습니다.',
  }[result.error.code] ?? '결제 처리 중 오류가 발생했습니다. 고객지원에 문의해 주세요.';
  
  setErrorMessage(userMessage);
  // 에러 로깅 (Sentry 등)
  captureException(result.error, { extra: { userId, planId } });
}
```

#### API 에러 UX

```typescript
// X — API 에러를 그냥 던짐 → 빈 화면 or 흰 화면
const { data } = await api.getDashboard();
return <Dashboard data={data} />;

// O — 에러 상태 명시적 처리
const { data, error, isLoading } = useDashboard();

if (isLoading) return <DashboardSkeleton />; // 로딩 UI
if (error) return (                           // 에러 UI
  <ErrorState
    message="데이터를 불러오지 못했습니다"
    retry={() => refetch()}                   // 재시도 버튼
  />
);
if (!data?.length) return <EmptyState />;    // 빈 상태 UI
return <Dashboard data={data} />;
```

#### 빈 상태 (Empty State) 누락

가장 자주 잊어버리는 케이스:
- 신규 가입자 — 데이터 없는 상태의 대시보드 (리스트가 비어있으면 아무것도 안 보임)
- 검색 결과 0건 (흰 화면 대신 "결과가 없습니다" 메시지)
- 삭제 후 목록이 비어있을 때
- 필터 적용 후 결과 없을 때

```tsx
// 체크: 모든 리스트 컴포넌트에 빈 상태 처리가 있는가?
{items.length === 0 ? (
  <EmptyState
    icon={<InboxIcon />}
    title="아직 데이터가 없습니다"
    description="첫 번째 항목을 추가해 보세요"
    action={<Button onClick={onCreate}>만들기</Button>}
  />
) : (
  items.map(item => <ItemCard key={item.id} item={item} />)
)}
```

#### 로딩 상태 누락

```tsx
// X — 버튼 클릭 후 아무 피드백 없음 → 사용자가 여러 번 클릭 → 중복 요청
<Button onClick={handleSubmit}>저장</Button>

// O — 로딩 상태 + 비활성화
<Button
  onClick={handleSubmit}
  disabled={isSubmitting}
  loading={isSubmitting}  // 스피너 표시
>
  {isSubmitting ? '저장 중...' : '저장'}
</Button>
```

#### GraphQL "200 OK 에러" 함정

```typescript
// X — status 200이니까 성공이라고 가정
const response = await fetch('/graphql', { ... });
const json = await response.json();
const data = json.data; // errors 배열 체크 안 함

// O — GraphQL은 항상 errors 배열 확인
const json = await response.json();
if (json.errors?.length > 0) {
  throw new GraphQLError(json.errors[0].message, json.errors);
}
const data = json.data;
```

#### 멀티테넌시 데이터 격리 버그

SaaS에서 가장 위험한 버그. 반드시 테스트:
```typescript
// 테스트 시나리오: 두 테넌트 계정으로 각각 로그인 후 교차 접근 시도
test('다른 테넌트 데이터에 접근 불가', async ({ page }) => {
  // 테넌트 A의 리소스 ID
  const tenantAResourceId = 'resource-a-001';
  
  // 테넌트 B로 로그인
  await loginAs('tenant-b-user@example.com');
  
  // 테넌트 A의 리소스 직접 URL 접근
  const response = await page.request.get(`/api/resources/${tenantAResourceId}`);
  expect(response.status()).toBe(403); // 403 또는 404 — 절대 200 안 됨
});
```
