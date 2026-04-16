"""
auto_publish.py — Layer 4-B: 콘텐츠 자동 발행

ops_loop.py가 생성한 콘텐츠를 각 채널에 자동 발행.
발행 큐 시스템 + 채널별 API 연동.

사용법:
    python -m core.auto_publish process_queue     # 큐에 있는 콘텐츠 발행
    python -m core.auto_publish status             # 발행 상태 확인
    python -m core.auto_publish add --channel blog --title "제목" --content "내용"

또는 코드에서:
    from core.auto_publish import PublishQueue, publish_all
    queue = PublishQueue()
    queue.add_blog(title, content, tags)
    publish_all(queue)
"""

import os
import sys
import json
import requests
import io
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

# Windows 인코딩 문제 해결
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── 설정 ──────────────────────────────────────────────────


class PublishChannel(Enum):
    """발행 채널."""
    BLOG = "blog"           # 네이버 블로그
    INSTAGRAM = "instagram"  # 인스타그램
    EMAIL = "email"          # 이메일 DM
    KAKAO = "kakao"          # 카카오톡 (큐만, 수동 발송)
    NAVER_CAFE = "naver_cafe"  # 네이버 카페


class PublishStatus(Enum):
    """발행 상태."""
    PENDING = "pending"      # 대기 중
    SCHEDULED = "scheduled"  # 예약됨
    PUBLISHED = "published"  # 발행됨
    FAILED = "failed"        # 실패
    WAITING_APPROVAL = "waiting_approval"  # 승인 대기


# ── 큐 아이템 ──────────────────────────────────────────────────


class PublishItem:
    """발행 큐 아이템."""

    def __init__(
        self,
        item_id: str,
        channel: PublishChannel,
        content: Dict,
        status: PublishStatus = PublishStatus.PENDING,
        created_at: Optional[str] = None,
        scheduled_at: Optional[str] = None,
        published_at: Optional[str] = None,
        error: Optional[str] = None,
    ):
        self.item_id = item_id
        self.channel = channel if isinstance(channel, PublishChannel) else PublishChannel(channel)
        self.content = content
        self.status = status if isinstance(status, PublishStatus) else PublishStatus(status)
        self.created_at = created_at or datetime.now().isoformat()
        self.scheduled_at = scheduled_at
        self.published_at = published_at
        self.error = error

    def to_dict(self) -> Dict:
        """딕셔너리로 변환."""
        return {
            "item_id": self.item_id,
            "channel": self.channel.value,
            "content": self.content,
            "status": self.status.value,
            "created_at": self.created_at,
            "scheduled_at": self.scheduled_at,
            "published_at": self.published_at,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PublishItem":
        """딕셔너리에서 생성."""
        return cls(
            item_id=data["item_id"],
            channel=data["channel"],
            content=data["content"],
            status=data.get("status", "pending"),
            created_at=data.get("created_at"),
            scheduled_at=data.get("scheduled_at"),
            published_at=data.get("published_at"),
            error=data.get("error"),
        )


# ── 큐 관리 ──────────────────────────────────────────────────


class PublishQueue:
    """발행 큐 관리."""

    def __init__(self, queue_file: Optional[str] = None):
        if queue_file is None:
            queue_file = os.path.join(os.path.dirname(__file__), "publish_queue.json")
        self.queue_file = queue_file
        self.items: List[PublishItem] = []
        self._load()

    def _load(self):
        """파일에서 로드."""
        if not os.path.exists(self.queue_file):
            self.items = []
            return
        try:
            with open(self.queue_file, encoding="utf-8") as f:
                data = json.load(f)
            self.items = [PublishItem.from_dict(item) for item in data.get("items", [])]
        except Exception as e:
            print(f"⚠️ 큐 로드 실패: {e}")
            self.items = []

    def _save(self):
        """파일에 저장."""
        try:
            data = {"items": [item.to_dict() for item in self.items]}
            with open(self.queue_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 큐 저장 실패: {e}")

    def add_blog(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        status: PublishStatus = PublishStatus.PENDING,
    ) -> PublishItem:
        """블로그 아이템 추가."""
        item_id = f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        item = PublishItem(
            item_id=item_id,
            channel=PublishChannel.BLOG,
            content={
                "title": title,
                "body": content,
                "tags": tags or [],
            },
            status=status,
        )
        self.items.append(item)
        self._save()
        return item

    def add_instagram(
        self,
        caption: str,
        image_url: Optional[str] = None,
        scheduled_at: Optional[str] = None,
        status: PublishStatus = PublishStatus.PENDING,
    ) -> PublishItem:
        """인스타그램 아이템 추가."""
        item_id = f"ig_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        item = PublishItem(
            item_id=item_id,
            channel=PublishChannel.INSTAGRAM,
            content={
                "caption": caption,
                "image_url": image_url,
            },
            status=status,
            scheduled_at=scheduled_at,
        )
        self.items.append(item)
        self._save()
        return item

    def add_email(
        self,
        to: str,
        subject: str,
        body: str,
        status: PublishStatus = PublishStatus.PENDING,
    ) -> PublishItem:
        """이메일 아이템 추가."""
        item_id = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        item = PublishItem(
            item_id=item_id,
            channel=PublishChannel.EMAIL,
            content={
                "to": to,
                "subject": subject,
                "body": body,
            },
            status=status,
        )
        self.items.append(item)
        self._save()
        return item

    def add_kakao(
        self,
        message: str,
        target_ids: Optional[List[str]] = None,
        status: PublishStatus = PublishStatus.PENDING,
    ) -> PublishItem:
        """카카오톡 아이템 추가 (큐만 저장, 실제 발송은 별도)."""
        item_id = f"kakao_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        item = PublishItem(
            item_id=item_id,
            channel=PublishChannel.KAKAO,
            content={
                "message": message,
                "target_ids": target_ids or [],
            },
            status=status,
        )
        self.items.append(item)
        self._save()
        return item

    def add_naver_cafe(
        self,
        title: str,
        content: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: PublishStatus = PublishStatus.PENDING,
    ) -> PublishItem:
        """네이버 카페 아이템 추가."""
        item_id = f"cafe_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        item = PublishItem(
            item_id=item_id,
            channel=PublishChannel.NAVER_CAFE,
            content={
                "title": title,
                "body": content,
                "category": category,
                "tags": tags or [],
            },
            status=status,
        )
        self.items.append(item)
        self._save()
        return item

    def get_pending(self) -> List[PublishItem]:
        """대기 중인 아이템 반환."""
        return [
            item for item in self.items
            if item.status in (PublishStatus.PENDING, PublishStatus.SCHEDULED)
        ]

    def update_status(self, item_id: str, status: PublishStatus, error: Optional[str] = None):
        """아이템 상태 업데이트."""
        for item in self.items:
            if item.item_id == item_id:
                item.status = status
                if status == PublishStatus.PUBLISHED:
                    item.published_at = datetime.now().isoformat()
                if error:
                    item.error = error
                self._save()
                return
        print(f"⚠️ 아이템을 찾을 수 없음: {item_id}")

    def remove(self, item_id: str):
        """아이템 제거."""
        self.items = [item for item in self.items if item.item_id != item_id]
        self._save()


# ── 발행 함수 ──────────────────────────────────────────────────


class BlogPublisher:
    """네이버 블로그 발행."""

    def __init__(self):
        self.client_id = os.getenv("NAVER_BLOG_CLIENT_ID")
        self.client_secret = os.getenv("NAVER_BLOG_CLIENT_SECRET")
        self.access_token = os.getenv("NAVER_BLOG_ACCESS_TOKEN")
        self.blog_id = os.getenv("NAVER_BLOG_ID")

    def is_configured(self) -> bool:
        """설정 확인."""
        return bool(self.access_token and self.blog_id)

    def publish(self, title: str, body: str, tags: Optional[List[str]] = None) -> Dict:
        """블로그 글 발행."""
        if not self.is_configured():
            return {
                "success": False,
                "error": "네이버 블로그 인증 정보 부재. 설정 가이드: SETUP_PUBLISH.md",
            }

        try:
            # 네이버 블로그 API: https://developers.naver.com/docs/blog/
            url = f"https://apis.naver.com/blog/v1/blog/{self.blog_id}/posts"

            # 마크다운을 HTML로 변환 (간단한 버전)
            html_body = body.replace("\n", "<br>")

            params = {
                "title": title,
                "content": html_body,
                "visibility": 0,  # 0=공개, 1=보호, 2=비공개
            }

            if tags:
                params["tags"] = ",".join(tags)

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            response = requests.post(url, json=params, headers=headers, timeout=10)

            if response.status_code == 201:
                data = response.json()
                return {
                    "success": True,
                    "post_id": data.get("id"),
                    "url": data.get("permalink"),
                    "message": f"블로그 발행 완료: {title}",
                }
            else:
                return {
                    "success": False,
                    "error": f"API 에러 {response.status_code}: {response.text}",
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"블로그 발행 실패: {str(e)}",
            }


class InstagramPublisher:
    """인스타그램 발행 (Meta Graph API)."""

    def __init__(self):
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.ig_business_account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

    def is_configured(self) -> bool:
        """설정 확인."""
        return bool(self.access_token and self.ig_business_account_id)

    def publish(self, caption: str, image_url: Optional[str] = None) -> Dict:
        """인스타그램 포스트 발행."""
        if not self.is_configured():
            return {
                "success": False,
                "error": "Meta Graph API 설정 부재. 설정 가이드: SETUP_PUBLISH.md",
            }

        if not image_url:
            return {
                "success": False,
                "error": "이미지 URL 필수. 대기열에 보관 중. 이미지 첨부 후 다시 시도해주세요.",
            }

        try:
            # Meta Graph API: https://developers.facebook.com/docs/instagram-api
            # 1. 미디어 객체 생성
            url = f"https://graph.instagram.com/v18.0/{self.ig_business_account_id}/media"

            params = {
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token,
            }

            response = requests.post(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                media_id = data.get("id")

                # 2. 미디어 퍼블리시
                publish_url = f"https://graph.instagram.com/v18.0/{self.ig_business_account_id}/media_publish"
                publish_params = {
                    "creation_id": media_id,
                    "access_token": self.access_token,
                }

                publish_response = requests.post(publish_url, params=publish_params, timeout=10)

                if publish_response.status_code == 200:
                    publish_data = publish_response.json()
                    return {
                        "success": True,
                        "post_id": publish_data.get("id"),
                        "message": f"인스타그램 발행 완료",
                    }
                else:
                    return {
                        "success": False,
                        "error": f"퍼블리시 실패 {publish_response.status_code}",
                    }
            else:
                return {
                    "success": False,
                    "error": f"미디어 생성 실패 {response.status_code}: {response.text}",
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"인스타그램 발행 실패: {str(e)}",
            }

    def schedule(self, caption: str, image_url: str, scheduled_at: str) -> Dict:
        """인스타그램 예약 포스트 (Business 계정 필수)."""
        # 실제 구현은 Meta API의 scheduling 엔드포인트 사용
        return {
            "success": False,
            "error": "예약 기능은 Meta Business 계정 전환 + 추가 권한 필요. 문의: 리안",
        }


class EmailPublisher:
    """이메일 발행 (Gmail SMTP)."""

    def __init__(self):
        self.gmail_address = os.getenv("GMAIL_ADDRESS")
        self.gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")

    def is_configured(self) -> bool:
        """설정 확인."""
        return bool(self.gmail_address and self.gmail_app_password)

    def publish(self, to: str, subject: str, body: str) -> Dict:
        """이메일 발송."""
        if not self.is_configured():
            return {
                "success": False,
                "error": "Gmail 설정 부재. 설정 가이드: SETUP_PUBLISH.md",
            }

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            # Gmail SMTP
            smtp_server = "smtp.gmail.com"
            smtp_port = 587

            # 메시지 작성
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.gmail_address
            msg["To"] = to

            # HTML 버전
            html_body = body.replace("\n", "<br>")
            part = MIMEText(html_body, "html")
            msg.attach(part)

            # 발송
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(self.gmail_address, self.gmail_app_password)
                server.send_message(msg)

            return {
                "success": True,
                "message": f"이메일 발송 완료: {to}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"이메일 발송 실패: {str(e)}",
            }


class KakaoPublisher:
    """카카오톡 발행 (큐만 관리, 실제 발송은 별도)."""

    def publish(self, message: str, target_ids: List[str]) -> Dict:
        """카카오톡 메시지 (대기열에만 보관)."""
        return {
            "success": True,
            "message": f"카카오톡 메시지 대기열에 추가됨. 수동 발송 또는 PC카톡 매크로 연동 필요.",
            "pending_targets": target_ids,
        }


# ── 발행 실행 ──────────────────────────────────────────────────


def publish_item(item: PublishItem, auto_approve: bool = False) -> bool:
    """단일 아이템 발행."""
    print(f"\n  📤 [{item.channel.value}] {item.item_id} 발행 중...")

    try:
        result = None

        if item.channel == PublishChannel.BLOG:
            publisher = BlogPublisher()
            result = publisher.publish(
                title=item.content["title"],
                body=item.content["body"],
                tags=item.content.get("tags"),
            )

        elif item.channel == PublishChannel.INSTAGRAM:
            publisher = InstagramPublisher()
            result = publisher.publish(
                caption=item.content["caption"],
                image_url=item.content.get("image_url"),
            )

        elif item.channel == PublishChannel.EMAIL:
            publisher = EmailPublisher()
            result = publisher.publish(
                to=item.content["to"],
                subject=item.content["subject"],
                body=item.content["body"],
            )

        elif item.channel == PublishChannel.KAKAO:
            publisher = KakaoPublisher()
            result = publisher.publish(
                message=item.content["message"],
                target_ids=item.content.get("target_ids", []),
            )

        else:
            result = {"success": False, "error": f"미지원 채널: {item.channel.value}"}

        if result and result.get("success"):
            print(f"    ✅ {result.get('message', '발행 완료')}")
            return True
        else:
            error = result.get("error", "알 수 없는 에러") if result else "결과 없음"
            print(f"    ❌ {error}")
            return False

    except Exception as e:
        print(f"    ❌ 예외: {str(e)}")
        return False


def publish_all(queue: PublishQueue, auto_approve: bool = False) -> Dict:
    """큐의 모든 발행 대기 아이템 발행."""
    pending_items = queue.get_pending()

    if not pending_items:
        print("📭 발행 대기 중인 콘텐츠 없음")
        return {"total": 0, "published": 0, "failed": 0}

    print(f"\n{'='*60}")
    print(f"📤 콘텐츠 자동 발행 시작 ({len(pending_items)}개 아이템)")
    print(f"{'='*60}")

    published_count = 0
    failed_count = 0
    failed_items = []

    for item in pending_items:
        if publish_item(item, auto_approve):
            queue.update_status(item.item_id, PublishStatus.PUBLISHED)
            published_count += 1
        else:
            failed_count += 1
            failed_items.append(item.item_id)
            queue.update_status(item.item_id, PublishStatus.FAILED)

    print(f"\n{'='*60}")
    print(f"📊 발행 결과: {published_count}개 성공, {failed_count}개 실패")
    if failed_items:
        print(f"⚠️  실패 아이템: {', '.join(failed_items)}")
    print(f"{'='*60}\n")

    return {
        "total": len(pending_items),
        "published": published_count,
        "failed": failed_count,
        "failed_items": failed_items,
    }


def show_queue_status(queue: PublishQueue):
    """큐 상태 출력."""
    print(f"\n{'='*60}")
    print(f"[Queue Status]")
    print(f"{'='*60}")

    if not queue.items:
        print("큐가 비어있습니다.")
        return

    # 상태별 분류
    by_status = {}
    for item in queue.items:
        status = item.status.value
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(item)

    for status, items in by_status.items():
        print(f"\n{status.upper()} ({len(items)}개):")
        for item in items:
            title = None
            if item.channel == PublishChannel.BLOG:
                title = item.content.get("title")
            elif item.channel == PublishChannel.INSTAGRAM:
                title = item.content.get("caption", "")[:50]
            elif item.channel == PublishChannel.EMAIL:
                title = item.content.get("subject")
            else:
                title = str(item.content)[:50]

            print(f"  - {item.item_id} ({item.channel.value})")
            if title:
                print(f"    제목: {title}")
            if item.error:
                print(f"    에러: {item.error}")

    print(f"\n{'='*60}\n")


# ── CLI ──────────────────────────────────────────────────────


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python -m core.auto_publish process_queue     # 큐 발행")
        print("  python -m core.auto_publish status             # 큐 상태 확인")
        sys.exit(1)

    command = sys.argv[1]
    queue = PublishQueue()

    if command == "process_queue":
        auto_approve = "--auto" in sys.argv
        result = publish_all(queue, auto_approve)
        print(f"최종 결과: {result}")

    elif command == "status":
        show_queue_status(queue)

    else:
        print(f"미지원 명령어: {command}")
