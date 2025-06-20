import os
import uuid
import qrcode
import hashlib
import logging
from django.db.models import Sum
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .models import Certificate, Lesson, Student
from rest_framework.test import APIRequestFactory

FONT_DIR = os.path.join(settings.BASE_DIR, "static", "fonts")
pdfmetrics.registerFont(TTFont("LibreBaskerville", os.path.join(FONT_DIR, "LibreBaskerville.ttf")))
pdfmetrics.registerFont(TTFont("Caladea", os.path.join(FONT_DIR, "Caladea.ttf")))


def generate_certificate(user, course, score):

    hash_code = hashlib.sha256(f"{user.id}-{course.id}-{user.username}".encode()).hexdigest()
    token = uuid.uuid4()

    verify_url = f"127.0.0.1:8000/certificate/verify/{token}/"

    qr_img = qrcode.make(verify_url)
    qr_io = BytesIO()
    qr_img.save(qr_io, format='PNG')
    qr_io.seek(0)
    qr_reader = ImageReader(qr_io)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    template_path = os.path.join(settings.MEDIA_ROOT, "certificates", "certificate_template.png")

    if os.path.exists(template_path):
        p.drawImage(template_path, 0, 0, width=width, height=height)

    p.setFont("LibreBaskerville", 24)
    p.drawString(350, 253, f"{user.username}")

    p.setFont("Caladea", 14)
    p.drawString(560, 220,  course.title)

    p.setFont("Times-Roman", 24)
    p.drawString(220, 120, f"{course.author.user.username}")

    p.drawImage(qr_reader, 551, 100, width=100, height=100)

    p.setFont("Times-Roman", 12)
    p.drawString(568, 90, user.date_joined.strftime('%Y-%m-%d'))

    p.showPage()
    p.save()

    buffer.seek(0)

    cert = Certificate.objects.create(
        user=user,
        course=course,
        token=token,
        hash_code=hash_code,
        score=score
    )
    file_name = f"certificate_{user.username}_{course.id}.pdf"
    cert.pdf_file.save(f"{file_name}", ContentFile(buffer.read()))
    return cert