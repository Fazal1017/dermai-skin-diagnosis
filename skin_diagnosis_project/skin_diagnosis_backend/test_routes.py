import os
import django
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skin_diagnosis_backend.settings")
django.setup()

client = Client()

urls_to_test = [
    '/',
    '/accounts/register/',
    '/accounts/login/',
    '/accounts/profile/',
    '/admin/'
]

for url in urls_to_test:
    try:
        response = client.get(url, HTTP_HOST='127.0.0.1')
        print(f"GET {url} -> Status Code: {response.status_code}")
        if response.status_code == 500:
            print("  Error content snippet:")
            print(response.content.decode()[:500])
    except Exception as e:
        print(f"GET {url} -> EXCEPTION: {e}")
