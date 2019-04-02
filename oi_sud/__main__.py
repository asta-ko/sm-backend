#!/usr/bin/env python
import os
import sys

C_PROJECT_STACK = os.environ.get('C_PROJECT_STACK', 'dev')

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'oi_sud.config.{C_PROJECT_STACK}')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            'available on your PYTHONPATH environment variable? Did you '
            'forget to activate a virtual environment?'
        ) from exc
    execute_from_command_line(sys.argv)
