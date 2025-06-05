import logging
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from allauth.account.signals import user_logged_in, user_signed_up
from .models import Course, Review, Student, MostPopularCourse, BestCourse, Author

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        Student.objects.get_or_create(user=instance)

@receiver(user_logged_in)
def login_success(sender, request, user, **kwargs):
    logger.info(f"User {user.email} has logged in!")

@receiver(user_signed_up)
def signup_success(sender, request, user, **kwargs):
    logger.info(f"New user signed up: {user.email}")

@receiver([post_save, post_delete], sender=Course)
@receiver([post_save, post_delete], sender=Student)
def update_most_popular_signal(sender, instance, **kwargs):
    MostPopularCourse.update_most_popular()

@receiver([post_save, post_delete], sender=Review)
def update_best_course_signal(sender, instance, **kwargs):
    BestCourse.update_best_course()

@receiver(post_delete, sender=Course)
def update_courses_on_delete(sender, instance, **kwargs):
    if BestCourse.objects.filter(course=instance).exists():
        BestCourse.update_best_course()
    if MostPopularCourse.objects.filter(course=instance).exists():
        MostPopularCourse.update_most_popular()

@receiver(post_save, sender=Author)
def sync_author_flags(sender, instance, **kwargs):
    updated = False

    if instance.author_status == "approved" and not instance.is_author:
        instance.is_author = True
        updated = True
    elif instance.author_status != "approved" and instance.is_author:
        instance.is_author = False
        updated = True

    if instance.journalist_status == "approved" and not instance.is_journalist:
        instance.is_journalist = True
        updated = True
    elif instance.journalist_status != "approved" and instance.is_journalist:
        instance.is_journalist = False
        updated = True

    if updated:
        from django.db.models.signals import post_save
        post_save.disconnect(sync_author_flags, sender=Author)
        instance.save()
        post_save.connect(sync_author_flags, sender=Author)