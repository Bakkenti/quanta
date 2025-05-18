from allauth.account.adapter import DefaultAccountAdapter

class MyAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        return f"https://jasulan273.github.io/Quanta/verify-email/?key={emailconfirmation.key}"
