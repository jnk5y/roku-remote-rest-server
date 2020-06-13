#!/usr/bin/env python3

import sys
import urllib.request

print(urllib.request.urlopen('https://localhost:8889/roku/health').getcode())

if urllib.request.urlopen('https://localhost:8889/roku/health').getcode() == 200:
    sys.exit(0)
else:
    sys.exit(1)
