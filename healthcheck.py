#!/usr/bin/env python3

import os
import sys
import urllib.request

print(urllib.request.urlopen(os.environ.get('HEALTHCHECK_URL')).getcode())

if urllib.request.urlopen(os.environ.get('HEALTHCHECK_URL')).getcode() == 200:
    sys.exit(0)
else:
    sys.exit(1)
