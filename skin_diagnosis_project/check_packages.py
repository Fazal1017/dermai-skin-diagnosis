#!/usr/bin/env python
import sys
packages = ['django', 'rest_framework', 'torch', 'numpy', 'PIL', 'sklearn', 'pandas', 'matplotlib', 'decouple', 'corsheaders']
print("Checking package imports:")
missing = []
for pkg in packages:
    try:
        if pkg == 'PIL':
            mod = __import__('PIL')
        else:
            mod = __import__(pkg)
        v = getattr(mod, '__version__', getattr(mod, 'VERSION', 'N/A'))
        print(f"  OK  {pkg:20} : {v}")
    except ImportError:
        print(f"  MISS {pkg:20} : NOT INSTALLED")
        missing.append(pkg)
    except Exception as e:
        print(f"  ERR {pkg:20} : {type(e).__name__}: {e}")

if missing:
    print(f"\nMissing packages: {', '.join(missing)}")
    sys.exit(1)
else:
    print("\nAll packages OK!")
    sys.exit(0)
