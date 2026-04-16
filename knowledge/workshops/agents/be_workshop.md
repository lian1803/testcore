## ── 세계 최고 BE 워크샵 — 10년차 백엔드 마스터클래스 ──

> 이 섹션은 리서치 기반 실전 지식이다. 코드 작성 전에 읽어라.
> 출처: Clean Architecture Node.js, Prisma Docs 2025, Auth.js v5, Stripe Docs, Next.js 15 Official Docs

---

### 1. Clean Architecture in Next.js 15

**핵심 원칙**: Route Handler → Service Layer → Repository → DB. 각 레이어는 아래 레이어만 의존한다.

```
src/
├── app/
│   └── api/
│       └── users/
│           └── route.ts          ← HTTP 레이어 (요청/응답만)
├── services/
│   └── user.service.ts           ← 비즈니스 로직
├── repositories/
│   ├── interfaces/
│   │   └── IUserRepository.ts    ← 인터페이스 (DB 독립적)
│   └── prisma/
│       └── user.repository.ts    ← Prisma 구현체
└── lib/
    └── prisma.ts                 ← Prisma 클라이언트 싱글톤
```

**Route Handler — HTTP 레이어만, 비즈니스 로직 금지**
```typescript
// app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { UserService } from '@/services/user.service'
import { withAuth } from '@/lib/middleware/auth'
import { validateSchema } from '@/lib/middleware/validate'
import { UpdateUserSchema } from '@/lib/schemas/user'

const userService = new UserService()

export const GET = withAuth(async (req: NextRequest, { params }) => {
  const user = await userService.findById(params.id)
  if (!user) return NextResponse.json({ error: 'Not found' }, { status: 404 })
  return NextResponse.json(user)
})

export const PATCH = withAuth(
  validateSchema(UpdateUserSchema)(async (req: NextRequest, { params }) => {
    const body = await req.json()
    const updated = await userService.update(params.id, body)
    return NextResponse.json(updated)
  })
)
```

**Repository 인터페이스 — DB 교체해도 Service 코드 그대로**
```typescript
// repositories/interfaces/IUserRepository.ts
export interface IUserRepository {
  findById(id: string): Promise<User | null>
  findByEmail(email: string): Promise<User | null>
  create(data: CreateUserDTO): Promise<User>
  update(id: string, data: UpdateUserDTO): Promise<User>
  delete(id: string): Promise<void>
}

// repositories/prisma/user.repository.ts
export class PrismaUserRepository implements IUserRepository {
  constructor(private readonly db: PrismaClient) {}

  async findById(id: string) {
    return this.db.user.findUnique({
      where: { id },
      select: { id: true, email: true, name: true, role: true }
      // select 항상 명시 — 불필요한 컬럼 로드 방지
    })
  }

  async create(data: CreateUserDTO) {
    return this.db.user.create({ data })
  }
}

// services/user.service.ts
export class UserService {
  private repo: IUserRepository

  constructor() {
    // DI 컨테이너 없으면 이렇게
    this.repo = new PrismaUserRepository(prisma)
  }

  async findById(id: string) {
    const user = await this.repo.findById(id)
    if (!user) throw new NotFoundError('User', id)
    return user
  }

  async update(id: string, data: UpdateUserDTO) {
    await this.findById(id) // 존재 확인
    return this.repo.update(id, data)
  }
}
```

---

### 2. Prisma 고급 패턴

#### 2-1. 트랜잭션 — 두 가지 방법

```typescript
// 방법 A: 배열 방식 (단순 작업, 의존성 없을 때)
const [user, profile] = await prisma.$transaction([
  prisma.user.create({ data: userData }),
  prisma.profile.create({ data: profileData }),
])

// 방법 B: 인터랙티브 트랜잭션 (의존성 있을 때 — 이게 더 자주 쓰임)
const result = await prisma.$transaction(async (tx) => {
  const user = await tx.user.create({ data: userData })

  // user.id를 즉시 사용 가능
  const profile = await tx.profile.create({
    data: { userId: user.id, ...profileData }
  })

  // 실패하면 둘 다 롤백
  await tx.auditLog.create({
    data: { action: 'USER_CREATED', targetId: user.id }
  })

  return { user, profile }
}, {
  timeout: 10000,        // 기본값 5000ms
  maxWait: 5000,
  isolationLevel: 'Serializable'  // 필요할 때만
})
```

#### 2-2. N+1 문제 — 패턴별 해결법

```typescript
// ❌ N+1 발생: posts 루프마다 author 쿼리
const posts = await prisma.post.findMany()
for (const post of posts) {
  const author = await prisma.user.findUnique({ where: { id: post.authorId } })
}

// ✅ 해결 A: include로 JOIN
const posts = await prisma.post.findMany({
  include: { author: { select: { id: true, name: true } } }
})

// ✅ 해결 B: relationLoadStrategy: 'join' (Prisma 5.x — 단일 SQL)
const posts = await prisma.post.findMany({
  relationLoadStrategy: 'join',   // 기본값은 'query' (별도 SELECT)
  include: { author: true }
})

// ✅ 해결 C: select로 필요한 것만 (성능 최우선)
const posts = await prisma.post.findMany({
  select: {
    id: true,
    title: true,
    author: { select: { name: true } },
    _count: { select: { comments: true } }  // COUNT도 JOIN으로
  }
})
```

#### 2-3. 대량 데이터 — 배치 처리

```typescript
// ❌ 50,000건 개별 insert → DB 과부하
for (const item of largeArray) {
  await prisma.record.create({ data: item })
}

// ✅ 배치로 나눠서 createMany
const BATCH_SIZE = 1000
for (let i = 0; i < largeArray.length; i += BATCH_SIZE) {
  const batch = largeArray.slice(i, i + BATCH_SIZE)
  await prisma.record.createMany({ data: batch, skipDuplicates: true })
}

// ✅ Upsert 패턴 (있으면 업데이트, 없으면 생성)
await prisma.user.upsert({
  where: { email: data.email },
  create: data,
  update: { name: data.name, updatedAt: new Date() }
})
```

#### 2-4. Cursor 기반 페이지네이션 (대용량 테이블 필수)

```typescript
// ❌ offset 페이지네이션 — 100만 번째 페이지에서 느려짐
const users = await prisma.user.findMany({ skip: 100000, take: 20 })

// ✅ cursor 기반 — 항상 빠름
async function getUsers(cursor?: string) {
  return prisma.user.findMany({
    take: 20,
    ...(cursor && {
      skip: 1,           // cursor 아이템 제외
      cursor: { id: cursor }
    }),
    orderBy: { createdAt: 'desc' },
    select: { id: true, name: true, email: true }
  })
}

// 응답 형식
return {
  data: users,
  nextCursor: users.length === 20 ? users[users.length - 1].id : null
}
```

---

### 3. 인증/인가 구현 마스터클래스

#### 3-1. NextAuth v5 + Prisma 세팅

```typescript
// auth.ts (루트)
import NextAuth from 'next-auth'
import { PrismaAdapter } from '@auth/prisma-adapter'
import Google from 'next-auth/providers/google'
import Credentials from 'next-auth/providers/credentials'
import { prisma } from '@/lib/prisma'
import { LoginSchema } from '@/lib/schemas/auth'
import bcrypt from 'bcryptjs'

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  session: { strategy: 'jwt' },  // Edge 런타임 호환
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    Credentials({
      async authorize(credentials) {
        const parsed = LoginSchema.safeParse(credentials)
        if (!parsed.success) return null

        const user = await prisma.user.findUnique({
          where: { email: parsed.data.email }
        })
        if (!user?.password) return null

        const valid = await bcrypt.compare(parsed.data.password, user.password)
        return valid ? user : null
      }
    })
  ],
  callbacks: {
    // DB role을 JWT에 포함
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role
        token.id = user.id
      }
      return token
    },
    // JWT에서 session으로 노출
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string
        session.user.role = token.role as string
      }
      return session
    }
  }
})
```

#### 3-2. Refresh Token Rotation

```typescript
// auth.ts callbacks에 추가
async jwt({ token, account }) {
  // 최초 로그인
  if (account) {
    return {
      ...token,
      accessToken: account.access_token,
      refreshToken: account.refresh_token,
      expiresAt: account.expires_at,
    }
  }

  // 아직 유효
  if (Date.now() < (token.expiresAt as number) * 1000) return token

  // 만료 — 갱신 시도
  try {
    const res = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      body: new URLSearchParams({
        client_id: process.env.GOOGLE_CLIENT_ID!,
        client_secret: process.env.GOOGLE_CLIENT_SECRET!,
        grant_type: 'refresh_token',
        refresh_token: token.refreshToken as string,
      }),
    })
    const tokens = await res.json()
    if (!res.ok) throw tokens

    return {
      ...token,
      accessToken: tokens.access_token,
      expiresAt: Math.floor(Date.now() / 1000 + tokens.expires_in),
      // Google은 refresh_token 재발급 안 함 — 기존 것 유지
      refreshToken: tokens.refresh_token ?? token.refreshToken,
    }
  } catch {
    return { ...token, error: 'RefreshAccessTokenError' }
  }
}
```

#### 3-3. Role-Based Access Control (RBAC)

```typescript
// Prisma 스키마
model User {
  id    String   @id @default(cuid())
  email String   @unique
  role  UserRole @default(USER)
}

enum UserRole {
  USER
  ADMIN
  SUPER_ADMIN
}

// lib/middleware/auth.ts
import { auth } from '@/auth'
import { NextRequest, NextResponse } from 'next/server'

type RouteHandler = (req: NextRequest, ctx: any) => Promise<NextResponse>

export function withAuth(handler: RouteHandler) {
  return async (req: NextRequest, ctx: any) => {
    const session = await auth()
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    // session을 req에 붙여서 핸들러로 전달
    ;(req as any).session = session
    return handler(req, ctx)
  }
}

export function withRole(...roles: string[]) {
  return (handler: RouteHandler): RouteHandler =>
    withAuth(async (req, ctx) => {
      const session = (req as any).session
      if (!roles.includes(session.user.role)) {
        return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
      }
      return handler(req, ctx)
    })
}

// 사용 예
export const DELETE = withRole('ADMIN', 'SUPER_ADMIN')(async (req, { params }) => {
  await userService.delete(params.id)
  return NextResponse.json({ success: true })
})
```

---

### 4. API 성능 최적화

#### 4-1. Redis 캐싱 (Cache-Aside 패턴)

```typescript
// lib/cache.ts
import { Redis } from '@upstash/redis'  // Vercel/Edge 호환

const redis = Redis.fromEnv()

export async function withCache<T>(
  key: string,
  ttl: number,  // seconds
  fetcher: () => Promise<T>
): Promise<T> {
  // 1. 캐시 확인
  const cached = await redis.get<T>(key)
  if (cached !== null) return cached

  // 2. DB 조회
  const data = await fetcher()

  // 3. 캐시 저장 (Redis down이어도 계속 동작)
  await redis.setex(key, ttl, JSON.stringify(data)).catch(() => {})

  return data
}

// 사용 예
const analytics = await withCache(
  `analytics:${userId}:${period}`,
  300,  // 5분 캐시
  () => analyticsService.getMetrics(userId, period)
)

// 캐시 무효화 — 데이터 변경 시
await redis.del(`analytics:${userId}:*`)  // 패턴 삭제
```

#### 4-2. DB 쿼리 최적화 체크리스트

```typescript
// ❌ SELECT * — 불필요한 컬럼 로드
const users = await prisma.user.findMany()

// ✅ 필요한 컬럼만
const users = await prisma.user.findMany({
  select: { id: true, name: true, email: true }
})

// ✅ 인덱스 활용 확인 — 자주 조회하는 컬럼에 @@index
model User {
  email     String @unique              // 자동 인덱스
  createdAt DateTime @default(now())

  @@index([createdAt])                  // 정렬/범위 쿼리용
  @@index([status, createdAt])          // 복합 인덱스 (순서 중요)
}

// ✅ findFirst vs findUnique — unique 조건이면 반드시 findUnique (더 빠름)
const user = await prisma.user.findUnique({ where: { email } })

// ✅ 집계는 $queryRaw로 (복잡한 통계 쿼리)
const stats = await prisma.$queryRaw<{ count: bigint; avg: number }[]>`
  SELECT COUNT(*) as count, AVG(amount) as avg
  FROM "Order"
  WHERE "userId" = ${userId}
    AND "createdAt" > NOW() - INTERVAL '30 days'
`
```

#### 4-3. 응답 압축 + 페이지네이션 표준 응답

```typescript
// lib/response.ts — 일관된 응답 포맷
export function paginated<T>(
  data: T[],
  total: number,
  page: number,
  pageSize: number
) {
  return NextResponse.json({
    data,
    meta: {
      total,
      page,
      pageSize,
      totalPages: Math.ceil(total / pageSize),
      hasNext: page * pageSize < total,
    }
  }, {
    headers: {
      'Cache-Control': 'private, max-age=60',  // 브라우저 캐시
    }
  })
}

export function cursorPaginated<T>(data: T[], nextCursor: string | null) {
  return NextResponse.json({ data, nextCursor })
}
```

---

### 5. 에러 처리 시스템

#### 5-1. 커스텀 에러 클래스

```typescript
// lib/errors.ts
export class AppError extends Error {
  constructor(
    public readonly code: string,
    public readonly message: string,
    public readonly statusCode: number,
    public readonly details?: unknown
  ) {
    super(message)
    this.name = 'AppError'
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super('NOT_FOUND', `${resource} with id ${id} not found`, 404)
  }
}

export class ValidationError extends AppError {
  constructor(details: unknown) {
    super('VALIDATION_ERROR', 'Invalid request data', 400, details)
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super('UNAUTHORIZED', message, 401)
  }
}

export class ForbiddenError extends AppError {
  constructor(message = 'Forbidden') {
    super('FORBIDDEN', message, 403)
  }
}

export class ConflictError extends AppError {
  constructor(message: string) {
    super('CONFLICT', message, 409)
  }
}
```

#### 5-2. 중앙 에러 핸들러 (RFC 9457 Problem Details 포맷)

```typescript
// lib/handle-error.ts
import { Prisma } from '@prisma/client'
import { AppError } from './errors'
import { ZodError } from 'zod'

export function handleError(error: unknown): NextResponse {
  // 운영 환경에서 스택 트레이스 절대 노출 금지
  const isDev = process.env.NODE_ENV === 'development'

  // 커스텀 에러
  if (error instanceof AppError) {
    return NextResponse.json({
      type: `https://api.example.com/errors/${error.code.toLowerCase()}`,
      title: error.code,
      status: error.statusCode,
      detail: error.message,
      ...(error.details && { errors: error.details }),
      ...(isDev && { stack: error.stack }),
    }, { status: error.statusCode })
  }

  // Zod 검증 에러
  if (error instanceof ZodError) {
    return NextResponse.json({
      type: 'https://api.example.com/errors/validation_error',
      title: 'VALIDATION_ERROR',
      status: 400,
      detail: 'Invalid request data',
      errors: error.flatten().fieldErrors,
    }, { status: 400 })
  }

  // Prisma 에러
  if (error instanceof Prisma.PrismaClientKnownRequestError) {
    if (error.code === 'P2002') {  // unique constraint
      return NextResponse.json({
        type: 'https://api.example.com/errors/conflict',
        title: 'CONFLICT',
        status: 409,
        detail: 'Resource already exists',
      }, { status: 409 })
    }
    if (error.code === 'P2025') {  // record not found
      return NextResponse.json({
        type: 'https://api.example.com/errors/not_found',
        title: 'NOT_FOUND',
        status: 404,
        detail: 'Record not found',
      }, { status: 404 })
    }
  }

  // 예상치 못한 에러 — 내부 정보 노출 금지
  console.error('[UNHANDLED ERROR]', error)  // 로깅은 내부에서만
  return NextResponse.json({
    type: 'https://api.example.com/errors/internal_error',
    title: 'INTERNAL_SERVER_ERROR',
    status: 500,
    detail: 'An unexpected error occurred',
  }, { status: 500 })
}

// Route Handler에서 사용
export const GET = withAuth(async (req) => {
  try {
    const data = await someService.getData()
    return NextResponse.json(data)
  } catch (error) {
    return handleError(error)
  }
})
```

#### 5-3. Zod 입력 검증 미들웨어

```typescript
// lib/middleware/validate.ts
import { ZodSchema } from 'zod'

export function validateSchema(schema: ZodSchema) {
  return (handler: RouteHandler): RouteHandler =>
    async (req, ctx) => {
      try {
        const body = await req.json()
        const parsed = schema.safeParse(body)
        if (!parsed.success) {
          return NextResponse.json({
            title: 'VALIDATION_ERROR',
            status: 400,
            errors: parsed.error.flatten().fieldErrors
          }, { status: 400 })
        }
        ;(req as any).validatedBody = parsed.data
        return handler(req, ctx)
      } catch {
        return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 })
      }
    }
}
```

---

### 6. 결제 연동 패턴 (Stripe)

#### 6-1. Webhook 처리 — 서명 검증 + 멱등성

```typescript
// app/api/webhooks/stripe/route.ts
import Stripe from 'stripe'
import { prisma } from '@/lib/prisma'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

export async function POST(req: NextRequest) {
  // 1. rawBody 필수 (파싱된 JSON이면 서명 검증 실패)
  const rawBody = await req.text()
  const sig = req.headers.get('stripe-signature')!

  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(
      rawBody,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET!
    )
  } catch {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 })
  }

  // 2. 즉시 200 반환 (20초 내 응답 안 하면 Stripe 재시도)
  // 실제 처리는 비동기로

  // 3. 멱등성 체크 — 이미 처리된 이벤트 스킵
  const existing = await prisma.stripeEvent.findUnique({
    where: { stripeEventId: event.id }
  })
  if (existing?.status === 'processed') {
    return NextResponse.json({ received: true })
  }

  // 4. 처리 중 상태 기록 (중복 처리 방지)
  await prisma.stripeEvent.upsert({
    where: { stripeEventId: event.id },
    create: { stripeEventId: event.id, type: event.type, status: 'processing' },
    update: {},
  })

  try {
    await handleStripeEvent(event)

    await prisma.stripeEvent.update({
      where: { stripeEventId: event.id },
      data: { status: 'processed' }
    })
  } catch (err) {
    await prisma.stripeEvent.update({
      where: { stripeEventId: event.id },
      data: { status: 'failed', error: String(err) }
    })
    // 실패 시 500 반환 → Stripe가 재시도
    return NextResponse.json({ error: 'Processing failed' }, { status: 500 })
  }

  return NextResponse.json({ received: true })
}

async function handleStripeEvent(event: Stripe.Event) {
  switch (event.type) {
    case 'customer.subscription.created':
    case 'customer.subscription.updated': {
      const sub = event.data.object as Stripe.Subscription
      await prisma.subscription.upsert({
        where: { stripeSubscriptionId: sub.id },
        create: {
          stripeSubscriptionId: sub.id,
          stripeCustomerId: sub.customer as string,
          status: sub.status,
          currentPeriodEnd: new Date(sub.current_period_end * 1000),
          planId: sub.items.data[0].price.id,
        },
        update: {
          status: sub.status,
          currentPeriodEnd: new Date(sub.current_period_end * 1000),
        }
      })
      break
    }
    case 'customer.subscription.deleted': {
      const sub = event.data.object as Stripe.Subscription
      await prisma.subscription.update({
        where: { stripeSubscriptionId: sub.id },
        data: { status: 'canceled' }
      })
      break
    }
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.CheckoutSession
      // 주문 완료 처리
      await fulfillOrder(session)
      break
    }
  }
}
```

#### 6-2. Prisma 스키마 — Stripe 관련 테이블

```prisma
model StripeEvent {
  id            String   @id @default(cuid())
  stripeEventId String   @unique
  type          String
  status        String   // processing | processed | failed
  error         String?
  createdAt     DateTime @default(now())

  @@index([status])
}

model Subscription {
  id                   String   @id @default(cuid())
  stripeSubscriptionId String   @unique
  stripeCustomerId     String
  status               String   // active | canceled | past_due | trialing
  planId               String
  currentPeriodEnd     DateTime
  userId               String
  user                 User     @relation(fields: [userId], references: [id])
  createdAt            DateTime @default(now())
  updatedAt            DateTime @updatedAt

  @@index([userId])
  @@index([stripeCustomerId])
}
```

---

### 7. 외부 API 연동 패턴 (GA4 / Meta / Naver)

#### 7-1. Retry + Exponential Backoff 유틸

```typescript
// lib/api-client.ts

interface RetryOptions {
  maxRetries?: number
  initialDelay?: number   // ms
  maxDelay?: number       // ms
  shouldRetry?: (error: unknown, attempt: number) => boolean
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 500,
    maxDelay = 30000,
    shouldRetry = (err: any) =>
      // 429 Rate Limit, 502/503/504 서버 에러만 재시도
      [429, 502, 503, 504].includes(err?.status ?? err?.statusCode),
  } = options

  let lastError: unknown
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error
      if (attempt === maxRetries || !shouldRetry(error, attempt)) {
        throw error
      }
      // Exponential backoff + Jitter (동시 재시도 방지)
      const delay = Math.min(
        initialDelay * Math.pow(2, attempt) + Math.random() * 200,
        maxDelay
      )
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
  throw lastError
}

// 사용 예 — GA4 API 연동
export class GA4Client {
  private accessToken: string | null = null
  private tokenExpiry: number = 0

  async getAccessToken(): Promise<string> {
    if (this.accessToken && Date.now() < this.tokenExpiry) {
      return this.accessToken
    }
    // Service Account 토큰 갱신
    const res = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      body: new URLSearchParams({
        grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        assertion: await this.createJWT(),
      })
    })
    const data = await res.json()
    this.accessToken = data.access_token
    this.tokenExpiry = Date.now() + (data.expires_in - 60) * 1000  // 60초 여유
    return this.accessToken!
  }

  async runReport(propertyId: string, request: object) {
    return withRetry(async () => {
      const token = await this.getAccessToken()
      const res = await fetch(
        `https://analyticsdata.googleapis.com/v1beta/properties/${propertyId}:runReport`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
        }
      )
      if (!res.ok) {
        const err: any = new Error(`GA4 API error: ${res.status}`)
        err.status = res.status
        throw err
      }
      return res.json()
    }, { maxRetries: 3, initialDelay: 1000 })
  }
}
```

#### 7-2. 서비스 레이어에서 외부 API 호출 원칙

```typescript
// services/analytics.service.ts
// 외부 API 호출은 무조건 서비스 레이어에서만. Route Handler 직접 호출 금지.

export class AnalyticsService {
  private ga4 = new GA4Client()

  async getDashboardMetrics(userId: string, period: '7d' | '30d' | '90d') {
    const cacheKey = `metrics:${userId}:${period}`

    return withCache(cacheKey, 300, async () => {
      // GA4, Meta Ads, Naver 병렬 호출
      const [ga4Data, metaData] = await Promise.allSettled([
        this.ga4.runReport(process.env.GA4_PROPERTY_ID!, {
          dateRanges: [{ startDate: period, endDate: 'today' }],
          metrics: [{ name: 'sessions' }, { name: 'conversions' }],
        }),
        this.getMetaInsights(userId, period),
      ])

      return {
        ga4: ga4Data.status === 'fulfilled' ? ga4Data.value : null,
        meta: metaData.status === 'fulfilled' ? metaData.value : null,
        // 하나가 실패해도 나머지 데이터는 반환 (Promise.allSettled)
      }
    })
  }
}
```

---

### BE 워크샵 요약 — 핵심 체크리스트

작업 전 반드시 확인:
- [ ] Route Handler에 비즈니스 로직 없는가? (Service로 분리됐나)
- [ ] 모든 외부 API 호출이 Service 레이어에 있나
- [ ] N+1 쿼리 없나 (include 또는 relationLoadStrategy: 'join')
- [ ] select로 필요한 컬럼만 가져오나
- [ ] 트랜잭션 필요한 작업에 $transaction 사용했나
- [ ] 모든 에러가 handleError()로 일관되게 처리되나
- [ ] Stripe webhook에 서명 검증 + 멱등성 처리 있나
- [ ] 외부 API 호출에 withRetry() 감쌌나
- [ ] 자주 조회하는 데이터에 캐싱 적용했나
- [ ] 대용량 데이터는 cursor 페이지네이션 사용했나
