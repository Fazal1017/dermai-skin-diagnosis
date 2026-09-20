import traceback, sys
try:
    import django
    get_v = getattr(django, 'get_version', None)
    v = get_v() if get_v else getattr(django, '__version__', 'unknown')
    print('DJANGO_VERSION:', v)
    print('DJANGO __file__:', getattr(django, '__file__', 'N/A'))
    import django.core.management as m
    print('django.core.management __file__:', getattr(m, '__file__', 'N/A'))
except Exception:
    traceback.print_exc()
    sys.exit(1)
