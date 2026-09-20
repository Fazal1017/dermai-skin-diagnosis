import importlib
import sys

packages = [
    ('django', 'Django'),
    ('rest_framework', 'Django REST framework'),
    ('corsheaders', 'django-cors-headers'),
    ('torch', 'torch'),
    ('torchvision', 'torchvision'),
    ('numpy', 'numpy'),
    ('PIL', 'Pillow'),
    ('sklearn', 'scikit-learn'),
    ('pandas', 'pandas'),
    ('matplotlib', 'matplotlib'),
    ('decouple', 'python-decouple'),
    ('gunicorn', 'gunicorn'),
]

print(f'Python: {sys.version}')
print(f'Executable: {sys.executable}')
print()

missing = []
for module_name, display_name in packages:
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', getattr(module, 'VERSION', 'unknown'))
        print(f'OK   {display_name:<24} {version}')
    except Exception as exc:
        print(f'FAIL {display_name:<24} {type(exc).__name__}: {exc}')
        missing.append(display_name)

print()
if missing:
    print('Missing or broken: ' + ', '.join(missing))
    raise SystemExit(1)
print('All required packages import successfully.')
