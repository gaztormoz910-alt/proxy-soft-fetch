"""Общая настройка тестов.

Корень репозитория добавляется в sys.path, чтобы `import fetch_proxy` / `import gui`
работали при запуске pytest из любой директории.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
