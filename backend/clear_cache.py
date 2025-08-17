#!/usr/bin/env python
"""
Clear Django Cache
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from django.core.cache import cache

def clear_cache():
    """Clear Django cache"""
    print("🧹 Clearing Django Cache...")
    cache.clear()
    print("✅ Cache cleared successfully!")

if __name__ == '__main__':
    clear_cache()
