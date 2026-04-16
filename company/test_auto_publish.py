"""
test_auto_publish.py — auto_publish.py 기능 테스트

사용법:
    python test_auto_publish.py --test-queue        # 큐 기능 테스트
    python test_auto_publish.py --test-all          # 모든 채널 테스트
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# 부모 디렉토리 추가
sys.path.insert(0, os.path.dirname(__file__))

from core.auto_publish import (
    PublishQueue,
    PublishChannel,
    PublishStatus,
    EmailPublisher,
    show_queue_status,
)

load_dotenv()


def test_queue():
    """큐 기능 테스트."""
    print("\n" + "="*60)
    print("Test 1: Queue Functions")
    print("="*60)

    queue = PublishQueue()

    print("\n[1] Adding blog item...")
    blog_item = queue.add_blog(
        title="[Test] 2026 Marketing Trends",
        content="Test blog post content.",
        tags=["test", "marketing"],
    )
    print(f"   Created: {blog_item.item_id}")

    print("\n[2] Adding Instagram item...")
    ig_item = queue.add_instagram(
        caption="#test #marketing\n\n2026 marketing trends!",
        image_url="https://via.placeholder.com/1080x1080?text=Test",
    )
    print(f"   Created: {ig_item.item_id}")

    print("\n[3] Adding email item...")
    email_item = queue.add_email(
        to="test@example.com",
        subject="Free 2026 Marketing Guide",
        body="Check our new guide!",
    )
    print(f"   Created: {email_item.item_id}")

    print("\n[4] Queue Status:")
    show_queue_status(queue)

    print("\n[OK] Queue test completed!")
    return True


def test_email():
    """Gmail 테스트."""
    print("\n" + "="*60)
    print("Test 2: Gmail Email")
    print("="*60)

    publisher = EmailPublisher()

    if not publisher.is_configured():
        print("\nWarning: Gmail not configured.")
        print("   Add to .env file:")
        print("   - GMAIL_ADDRESS=your-email@gmail.com")
        print("   - GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx")
        return False

    print("\n[1] Preparing test email...")
    test_email_to = os.getenv("GMAIL_ADDRESS", "test@example.com")
    result = publisher.publish(
        to=test_email_to,
        subject="[Auto Publish] Test Email",
        body="This is a test email.",
    )

    print(f"\n[2] Result:")
    if result.get("success"):
        print(f"   OK: {result.get('message')}")
        print(f"   To: {test_email_to}")
    else:
        print(f"   FAIL: {result.get('error')}")

    return result.get("success", False)


def run_all_tests():
    """모든 테스트 실행."""
    print("\n" + "="*60)
    print("Running All Tests")
    print("="*60)

    results = {
        "queue": test_queue(),
        "email": test_email(),
    }

    # Summary
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    print(f"Queue: {'OK' if results['queue'] else 'FAIL'}")
    print(f"Gmail: {'OK' if results['email'] else 'NOT CONFIGURED'}")

    passed = sum(1 for v in results.values() if v)
    print(f"\nPassed: {passed}/{len(results)} tests")

    if passed == len(results):
        print("\nAll settings are configured!")
        print("Run: python -m core.auto_publish process_queue")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_auto_publish.py --test-queue")
        print("  python test_auto_publish.py --test-all")
        sys.exit(1)

    command = sys.argv[1]

    if command == "--test-queue":
        test_queue()
    elif command == "--test-all":
        run_all_tests()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
