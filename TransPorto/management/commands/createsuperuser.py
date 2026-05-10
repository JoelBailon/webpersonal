from django.contrib.auth.management.commands.createsuperuser import Command as CreateSuperUserCommand
from django.contrib.auth import get_user_model
from django.core.management import CommandError
from django.utils.termcolors import color_style
from django.core.management.base import CommandError

class Command(CreateSuperUserCommand):

    def handle(self, *args, **options):
        UserModel = get_user_model()
        username_field = UserModel.USERNAME_FIELD

        # Pedir datos básicos
        username = options.get('username')
        email = options.get('email') or options.get('correo_electronico')
        password = options.get('password')

        # Forzar a que siempre se pregunte contraseña
        if not password:
            from getpass import getpass
            while True:
                password = getpass('Contraseña: ')
                password2 = getpass('Confirmar contraseña: ')
                if password != password2:
                    self.stderr.write("Error: las contraseñas no coinciden. Intenta de nuevo.")
                elif not password:
                    self.stderr.write("Error: la contraseña no puede estar vacía.")
                else:
                    break

        # Validar campos requeridos
        if not username:
            username = input(f'{username_field}: ')
        if not email:
            email = input('Correo electrónico: ')

        # Crear superusuario con contraseña
        try:
            UserModel._default_manager.db_manager().create_superuser(
                nombre_usuario=username,
                correo_electronico=email,
                contraseña=password
            )
            self.stdout.write(self.style.SUCCESS('Superusuario creado correctamente.'))
        except Exception as e:
            raise CommandError(f'Error al crear superusuario: {e}')
