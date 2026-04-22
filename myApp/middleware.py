import ipaddress
import time

import requests
from django.conf import settings
from django.db.models import F
from django.utils import timezone

from .models import StudentIPLog


class StudentIPTrackingMiddleware:
    """
    Track student IP/location access records for dashboard monitoring.
    """

    SESSION_PREFIX = "student_ip_track_"
    THROTTLE_SECONDS = 300  # write at most once per 5 minutes per IP per session

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, "ENABLE_IP_TRACKING", True):
            return self.get_response(request)
        self._track_student_request(request)
        return self.get_response(request)

    def _track_student_request(self, request):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return
        if user.is_staff or user.is_superuser:
            return

        path = request.path or ""
        if path.startswith("/static/") or path.startswith("/media/") or path.startswith("/admin/"):
            return

        ip_address = self._get_client_ip(request)
        if not ip_address:
            return

        throttle_key = f"{self.SESSION_PREFIX}{ip_address}"
        now_ts = int(time.time())
        last_ts = int(request.session.get(throttle_key, 0) or 0)
        if now_ts - last_ts < self.THROTTLE_SECONDS:
            return
        request.session[throttle_key] = now_ts

        is_private_ip = self._is_private_ip(ip_address)
        country = ""
        region = ""
        city = ""
        if not is_private_ip:
            country, region, city = self._resolve_location(ip_address)

        defaults = {
            "country": country,
            "region": region,
            "city": city,
            "is_private_ip": is_private_ip,
            "last_path": path[:300],
            "user_agent": (request.META.get("HTTP_USER_AGENT", "") or "")[:1000],
        }
        log, created = StudentIPLog.objects.get_or_create(
            user=user,
            ip_address=ip_address,
            date_bucket=timezone.localdate(),
            defaults=defaults,
        )
        if not created:
            StudentIPLog.objects.filter(pk=log.pk).update(
                hit_count=F("hit_count") + 1,
                country=country or log.country,
                region=region or log.region,
                city=city or log.city,
                is_private_ip=is_private_ip,
                last_path=defaults["last_path"],
                user_agent=defaults["user_agent"],
                last_seen=timezone.now(),
            )

    @staticmethod
    def _get_client_ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return (request.META.get("REMOTE_ADDR") or "").strip()

    @staticmethod
    def _is_private_ip(ip_address):
        try:
            parsed = ipaddress.ip_address(ip_address)
            return (
                parsed.is_private
                or parsed.is_loopback
                or parsed.is_link_local
                or parsed.is_reserved
                or parsed.is_multicast
            )
        except ValueError:
            return False

    @staticmethod
    def _resolve_location(ip_address):
        try:
            response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=1.5)
            if response.status_code != 200:
                return "", "", ""
            data = response.json() or {}
            return (
                (data.get("country_name") or "")[:100],
                (data.get("region") or "")[:100],
                (data.get("city") or "")[:100],
            )
        except Exception:
            return "", "", ""
