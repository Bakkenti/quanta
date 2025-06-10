from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main.models import Student
from blog.models import BlogComment

class Command(BaseCommand):
    help = "Удаляет пользователей, ожидающих удаления более 7 дней"

    def handle(self, *args, **options):
        week_ago = timezone.now() - timedelta(days=7)
        students = Student.objects.filter(
            is_scheduled_for_de
