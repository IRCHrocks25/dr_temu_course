from __future__ import annotations

from datetime import datetime
from io import BytesIO
import os
import tempfile

import cloudinary
import cloudinary.uploader
import fitz
import qrcode
import requests
from django.conf import settings
from django.utils import timezone


DEFAULT_CERTIFICATE_TEMPLATE_URL = (
    "https://res.cloudinary.com/dcuswyfur/image/upload/v1776502363/"
    "KATALYST_-_Certificate_ohfqu6.pdf"
)


def _build_certificate_id(course_slug: str, user_id: int, issued_at: datetime) -> str:
    return f"CERT-{course_slug.upper()}-{user_id}-{issued_at.strftime('%Y%m%d')}"


def _build_verification_url(certificate_id: str) -> str:
    # Falls back safely in local/dev.
    base_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8001").rstrip("/")
    return f"{base_url}/verify-certificate/{certificate_id}/"


def _download_template(template_url: str) -> str:
    response = requests.get(template_url, timeout=20)
    response.raise_for_status()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(response.content)
    temp_file.close()
    return temp_file.name


def _overlay_certificate_data(
    template_path: str,
    user_name: str,
    course_name: str,
    issued_at: datetime,
    certificate_id: str,
    verification_url: str,
) -> BytesIO:
    doc = fitz.open(template_path)
    page = doc[0]
    page_rect = page.rect
    center_x = page_rect.width / 2

    date_str = issued_at.strftime("%B %d, %Y")

    # Coordinates tuned to current template proportions.
    field_positions = {
        "date": (page_rect.width * 0.14, page_rect.height * 0.12),
        "certificate_id": (page_rect.width * 0.14, page_rect.height * 0.78),
        # Raised slightly for better visual balance on this template.
        "student_name": (center_x, page_rect.height * 0.52),
        # Centered horizontally and kept at the current lower baseline.
        "course_name": (center_x, page_rect.height * 0.71),
    }

    text_fields = {
        "student_name": user_name,
        "course_name": course_name,
        "date": date_str,
        "certificate_id": certificate_id,
    }

    styles = {
        "student_name": {"fontsize": 28, "centered": True, "color": (1, 1, 1)},
        "course_name": {"fontsize": 18, "centered": True, "color": (1, 1, 1)},
        "date": {"fontsize": 11, "centered": False, "color": (1, 1, 1)},
        "certificate_id": {"fontsize": 9, "centered": False, "color": (1, 1, 1)},
    }

    def _insert_text(point: fitz.Point, text_value: str, size: int, color: tuple[float, float, float]) -> None:
        """
        Insert text using a built-in font first, then fallback.
        Some PyMuPDF builds fail on "times" unless an external font file is provided.
        """
        try:
            page.insert_text(
                point,
                text_value,
                fontsize=size,
                color=color,
                fontname="helv",
            )
        except Exception:
            # Fallback to default font resolution if explicit font binding fails.
            page.insert_text(
                point,
                text_value,
                fontsize=size,
                color=color,
            )

    for field_name, text in text_fields.items():
        if not text:
            continue
        x, y = field_positions[field_name]
        style = styles[field_name]
        if style["centered"]:
            estimated_width = len(text) * (style["fontsize"] * 0.6)
            point = fitz.Point(x - estimated_width / 2, y)
            _insert_text(point, text, style["fontsize"], style["color"])
        else:
            _insert_text(fitz.Point(x, y), text, style["fontsize"], style["color"])

    # Add QR code for verification.
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    qr_size = 100
    qr_x = (page_rect.width - qr_size) / 2
    qr_y = page_rect.height * 0.72
    page.insert_image(
        fitz.Rect(qr_x, qr_y, qr_x + qr_size, qr_y + qr_size),
        stream=qr_buffer.getvalue(),
    )

    output = BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    return output


def _configure_cloudinary_if_needed() -> None:
    cfg = cloudinary.config()
    if cfg.cloud_name:
        return

    cloudinary.config(
        cloud_name=getattr(settings, "CLOUDINARY_CLOUD_NAME", None) or os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=getattr(settings, "CLOUDINARY_API_KEY", None) or os.getenv("CLOUDINARY_API_KEY"),
        api_secret=getattr(settings, "CLOUDINARY_API_SECRET", None) or os.getenv("CLOUDINARY_API_SECRET"),
    )


def _upload_certificate_pdf(pdf_buffer: BytesIO, course_slug: str, certificate_id: str) -> dict | None:
    try:
        _configure_cloudinary_if_needed()
        result = cloudinary.uploader.upload(
            pdf_buffer,
            resource_type="raw",
            folder=f"certificates/{course_slug}",
            public_id=certificate_id.lower(),
            format="pdf",
            overwrite=True,
        )
        return {
            "certificate_url": result.get("secure_url"),
            "public_id": result.get("public_id"),
        }
    except Exception:
        return None


def generate_course_certificate(user, course, issued_at=None, template_url: str = DEFAULT_CERTIFICATE_TEMPLATE_URL):
    """
    Generate certificate from PDF template and upload to Cloudinary.
    Returns dict with certificate_id/certificate_url, or None if generation fails.
    """
    issued_at = issued_at or timezone.now()
    certificate_id = _build_certificate_id(course.slug, user.id, issued_at)
    verification_url = _build_verification_url(certificate_id)
    user_name = user.get_full_name().strip() or user.username

    template_path = None
    try:
        template_path = _download_template(template_url)
        pdf_buffer = _overlay_certificate_data(
            template_path=template_path,
            user_name=user_name,
            course_name=course.name,
            issued_at=issued_at,
            certificate_id=certificate_id,
            verification_url=verification_url,
        )
        upload_data = _upload_certificate_pdf(pdf_buffer, course.slug, certificate_id)
        if not upload_data or not upload_data.get("certificate_url"):
            return None
        return {
            "certificate_id": certificate_id,
            "certificate_url": upload_data["certificate_url"],
            "public_id": upload_data.get("public_id"),
        }
    except Exception:
        # Never break lesson completion if certificate rendering/upload fails.
        return None
    finally:
        if template_path and os.path.exists(template_path):
            try:
                os.remove(template_path)
            except OSError:
                pass
