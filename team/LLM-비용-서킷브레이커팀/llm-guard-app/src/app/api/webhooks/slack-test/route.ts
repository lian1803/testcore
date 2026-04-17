import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';


const testSchema = z.object({
  slack_webhook: z.string().url(),
});

// SSRF 방지: Slack 웹훅 URL만 허용
function isAllowedSlackUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return (
      parsed.protocol === 'https:' &&
      (parsed.hostname === 'hooks.slack.com' ||
        parsed.hostname.endsWith('.hooks.slack.com'))
    );
  } catch {
    return false;
  }
}

// POST /api/webhooks/slack-test — Slack 웹훅 테스트
export async function POST(request: NextRequest) {

  try {
    const body = testSchema.parse(await request.json());

    // SSRF 방지: 허용된 도메인만 요청 전송
    if (!isAllowedSlackUrl(body.slack_webhook)) {
      return NextResponse.json(
        { error: { code: 'INVALID_WEBHOOK_URL', message: 'Only hooks.slack.com URLs are allowed' } },
        { status: 400 }
      );
    }

    // Slack 메시지 전송
    const response = await fetch(body.slack_webhook, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: '🔔 LLM Guard Test Notification',
        blocks: [
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: '*LLM Guard - Test Alert*\n\nThis is a test notification from LLM Guard. Your Slack integration is working correctly!',
            },
          },
        ],
      }),
    });

    if (!response.ok) {
      return NextResponse.json(
        {
          error: {
            code: 'SLACK_ERROR',
            message: 'Failed to send Slack message',
          },
        },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { data: { message: 'Test notification sent successfully' } },
      { status: 200 }
    );
  } catch (error) {
    console.error('[Slack Test Error]', error);
    return NextResponse.json(
      {
        error: {
          code: 'INTERNAL_ERROR',
          message: 'Internal server error',
        },
      },
      { status: 500 }
    );
  }
}
