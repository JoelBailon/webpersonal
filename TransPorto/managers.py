from django.contrib.auth.models import BaseUserManager

class ClienteManager(BaseUserManager):
    def create_user(self, nombre_usuario, correo_electronico, password=None, **extra_fields):
        if not nombre_usuario:
            raise ValueError('El campo Nombre de Usuario debe ser establecido')
        if not correo_electronico:
            raise ValueError('El campo Correo Electrónico debe ser establecido')

        user = self.model(
            nombre_usuario=nombre_usuario,
            correo_electronico=self.normalize_email(correo_electronico),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nombre_usuario, correo_electronico, password=None, **extra_fields):
        user = self.create_user(
            nombre_usuario,
            correo_electronico,
            password=password,
            **extra_fields
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user
