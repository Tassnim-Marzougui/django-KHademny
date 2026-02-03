# test_email.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helloword.settings')
django.setup()

from django.core.mail import send_mail

send_mail(
    'Test email from Khademny',
    'Ceci est un email de test.',
    'noreply@khademny.com',
    ['tassnim.marzougui@isimg.tn'],
    fail_silently=False,
)
print("Email envoyé avec succès!")