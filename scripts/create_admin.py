import os
import sys
import pathlib
import django

# Ensure project root is on sys.path so Django settings can be imported
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_furgones.settings')
django.setup()

from django.contrib.auth import get_user_model

username = 'Admin GF'
password = 'MDN2025'

User = get_user_model()
user, created = User.objects.get_or_create(
    username=username,
    defaults={'email': 'admin@gf.local', 'is_superuser': True, 'is_staff': True},
)
user.is_superuser = True
user.is_staff = True
user.set_password(password)
user.save()
print(('Created' if created else 'Updated'), username)
