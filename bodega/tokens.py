# from django.contrib.auth.tokens import PasswordResetTokenGenerator

# class CustomTokenGenerator(PasswordResetTokenGenerator):
#     def _make_hash_value(self, user, timestamp):
#         login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
#         return f"{user.pk}{user.password}{login_timestamp}{user.is_active}{timestamp}"

# token_generator = CustomTokenGenerator()