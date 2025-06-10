import logging
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from allauth.account.signals import user_logged_in, user_signed_up
from .models import Course, Review, Student, MostPopularCourse, BestCourse, Author, CourseProgress, LessonProgress, Lesson, Moderator, Module, FinalExam, FinalExamAttempt
from exercises.models import Exercise, LessonAttempt
from django.utils import timezone
from decimal import Decimal
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

@receiver(post_save, sender=Moderator)
def set_student_role_to_moderator(sender, instance, created, **kwargs):
    if created and instance.student:
        instance.student.role = "moderator"
        instance.student.save()

@receiver(post_delete, sender=Moderator)
def remove_student_moderator_role(sender, instance, **kwargs):
    if instance.student and instance.student.role == "moderator":
        instance.student.role = "student"
        instance.student.save()


def recalc_lesson_progress(student, lesson):
    lp, _ = LessonProgress.objects.get_or_create(student=student, lesson=lesson)
    is_viewed = lp.is_viewed

    exercises = Exercise.objects.filter(lesson=lesson)
    total_exercises = exercises.count()
    completed_exercises = 0

    if total_exercises:
        last_attempt = LessonAttempt.objects.filter(student=student, lesson=lesson).order_by('-created_at').first()
        if last_attempt:
            completed_exercises = sum([res.get("is_correct") for res in last_attempt.answers if res.get("is_correct")])
    else:
        completed_exercises = 0

    if not is_viewed and total_exercises == 0:
        percent = Decimal("0.0")
    elif total_exercises == 0:
        percent = Decimal("100.0") if is_viewed else Decimal("0.0")
    else:
        percent = Decimal("0.0")
        if is_viewed:
            percent += Decimal("40.0")
        if total_exercises > 0:
            percent += Decimal("60.0") * Decimal(completed_exercises) / Decimal(total_exercises)
    lp.progress_percent = round(percent, 2)
    lp.is_completed = (lp.progress_percent == Decimal("100.0"))
    lp.completed_at = timezone.now() if lp.is_completed else None
    lp.save()
    recalc_course_progress(student, lesson.module.course)


def recalc_course_progress(student, course):
    lessons = Lesson.objects.filter(module__course=course)
    total_lessons = lessons.count()
    lesson_progress = LessonProgress.objects.filter(student=student, lesson__in=lessons)
    progress_sum = sum([lp.progress_percent for lp in lesson_progress])

    if total_lessons == 0:
        percent = Decimal("0.0")
    else:
        percent = progress_sum / Decimal(total_lessons)

    cp, _ = CourseProgress.objects.get_or_create(student=student, course=course)
    cp.progress_percent = round(percent, 2)
    cp.is_completed = (cp.progress_percent == Decimal("100.0"))
    cp.completed_at = timezone.now() if cp.is_completed else None
    cp.save()


@receiver(post_save, sender=LessonProgress)
def handle_lesson_progress_update(sender, instance, **kwargs):
    recalc_course_progress(instance.student, instance.lesson.module.course)

@receiver(post_save, sender=Lesson)
@receiver(post_delete, sender=Lesson)
def handle_lesson_changed(sender, instance, **kwargs):
    print(f"handle_lesson_changed triggered for Lesson {instance.id}")
    course = instance.module.course
    students = course.students.all()
    for student in students:
        print(f"Recalculating course progress for student {student.id}")
        recalc_course_progress(student, course)

@receiver(post_save, sender=Module)
@receiver(post_delete, sender=Module)
def handle_module_changed(sender, instance, **kwargs):
    course = instance.course
    students = course.students.all()
    for student in students:
        recalc_course_progress(student, course)

@receiver([post_save, post_delete], sender=Exercise)
def handle_exercise_changed(sender, instance, **kwargs):
    lesson = instance.lesson
    course = lesson.module.course
    students = course.students.all()
    for student in students:
        recalc_lesson_progress(student, lesson)

@receiver(post_save, sender=FinalExam)
def update_attempts_on_exam_change(sender, instance, created, **kwargs):
    if not created:
        max_attempts = instance.max_attempts
        for attempt in FinalExamAttempt.objects.filter(exam=instance):
            if attempt.attempt_number > max_attempts:
                attempt.delete()