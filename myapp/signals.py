ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_REQUIRED = False
from django.dispatch import receiver
from allauth.account.signals import user_logged_in, user_signed_up
import logging

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def login_success(sender, request, user, **kwargs):
    print(f"✅ User {user.email} has logged in!")
    logger.info(f"✅ User {user.email} has logged in!")

@receiver(user_signed_up)
def signup_success(sender, request, user, **kwargs):
    print(f"🎉 New user signed up: {user.email}")
    logger.info(f"🎉 New user signed up: {user.email}")
