from otp.ai.passlib.context import CryptContext
from otp.ai.passlib.ext.django.utils import DjangoContextAdapter
__all__ = [
 'password_context']
adapter = DjangoContextAdapter()
password_context = adapter.context
context_changed = adapter.reset_hashers
adapter.load_model()