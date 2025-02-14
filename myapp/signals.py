import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from allauth.account.signals import user_logged_in, user_signed_up
from .models import Course, Review, Student, MostPopularCourse, BestCourse

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def login_success(sender, request, user, **kwargs):
    logger.info(f"User {user.email} has logged in!")

@receiver(user_signed_up)
def signup_success(sender, request, user, **kwargs):
    logger.info(f"New user signed up: {user.email}")

@receiver(post_save, sender=Course)
@receiver(post_delete, sender=Course)
@receiver(post_save, sender=Student)
@receiver(post_delete, sender=Student)
def update_most_popular_signal(sender, instance, **kwargs):
    MostPopularCourse.update_most_popular()

@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_best_course_signal(sender, instance, **kwargs):
    BestCourse.update_best_course()

@receiver(post_delete, sender=Course)
def update_courses_on_delete(sender, instance, **kwargs):
    if BestCourse.objects.filter(course=instance).exists():
        BestCourse.update_best_course()
    if MostPopularCourse.objects.filter(course=instance).exists():
        MostPopularCourse.update_most_popular()
