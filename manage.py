#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Aumenta el límite de recursión si es necesario
sys.setrecursionlimit(1500)

def main():
    """Run administrative tasks."""
    # Establece la configuración del módulo Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webpersonal.settings')
    
    try:
        # Importa y ejecuta la línea de comandos de gestión de Django
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Ejecuta el comando de línea proporcionado
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()

    
#cd webpersonal
#python manage.py runserver 0.0.0.0:8000