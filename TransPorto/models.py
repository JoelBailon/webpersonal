from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random
import string
import datetime
from django.utils import timezone
from decimal import Decimal


class ClienteManager(BaseUserManager):
    def create_user(self, nombre_usuario, correo_electronico, password=None, **extra_fields):
        if not nombre_usuario:
            raise ValueError('El nombre de usuario es obligatorio')
        if not correo_electronico:
            raise ValueError('El correo electrónico es obligatorio')

        correo_electronico = self.normalize_email(correo_electronico)
        user = self.model(nombre_usuario=nombre_usuario, correo_electronico=correo_electronico, **extra_fields)
        user.set_password(password)  # Aquí se hashea la contraseña
        user.save(using=self._db)
        return user

    def create_superuser(self, nombre_usuario, correo_electronico, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)  # Muy importante

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(nombre_usuario, correo_electronico, password, **extra_fields)


class Cliente(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    sexo = models.CharField(max_length=10)  # Ajusta según opciones reales
    fecha_nacimiento = models.DateField(null=True, blank=True)
    direccion = models.CharField(max_length=255)
    numero_telefonico = models.CharField(max_length=20)
    correo_electronico = models.EmailField(unique=True)
    nombre_usuario = models.CharField(max_length=150, unique=True)
    foto_rostro = models.ImageField(upload_to='rostros/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = ClienteManager()

    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['correo_electronico']

    def __str__(self):
        return self.nombre_usuario
    
    TEMA_CHOICES = [
        ('light', 'Claro'),
        ('dark', 'Oscuro'),
    ]
    tema_preferido = models.CharField(max_length=10, choices=TEMA_CHOICES, default='light')
    orden_botones_inicio = models.JSONField(default=list, blank=True, null=True)


class CooperativaTransporte(models.Model):
    id_cooperativa = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    informacion_contacto = models.CharField(max_length=255)
    n_vehiculos = models.IntegerField()
    color_vehiculo = models.CharField(max_length=50)
    monto_a_cobrar = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre


class UnidadTransporte(models.Model):
    id_unidad = models.AutoField(primary_key=True)
    placa = models.CharField(max_length=10)
    detalles_de_ruta = models.CharField(max_length=150)
    id_cooperativa = models.ForeignKey('CooperativaTransporte', on_delete=models.CASCADE)

    def __str__(self):
        return self.placa


class Rutas(models.Model):
    id_rutas = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=150)
    hora = models.TimeField()
    id_unidad = models.ForeignKey('UnidadTransporte', on_delete=models.CASCADE)
    id_cooperativa = models.ForeignKey('CooperativaTransporte', on_delete=models.CASCADE)

    def __str__(self):
        return self.descripcion


class Conductores(models.Model):
    id_conductor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    numero_licencia = models.CharField(max_length=20)
    id_cooperativa = models.ForeignKey('CooperativaTransporte', on_delete=models.CASCADE)
    informacion_contacto = models.CharField(max_length=255)
    id_unidad = models.ForeignKey('UnidadTransporte', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Tarjeta(models.Model):
    id_tarjeta = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    numero_tarjeta = models.CharField(max_length=16, unique=True, blank=True)
    fecha_expiracion = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=10, default="Inactiva")
    saldo_asociado = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    codigo_seguridad = models.CharField(max_length=3, default='000', unique=True)
    fecha_emision = models.DateField(default=timezone.now)

    def generar_numero_tarjeta(self):
        return ''.join(random.choices(string.digits, k=16))

    def generar_codigo_seguridad(self):
        return ''.join(random.choices(string.digits, k=3))

    def save(self, *args, **kwargs):
        if not self.numero_tarjeta:
            self.numero_tarjeta = self.generar_numero_tarjeta()
        if not self.fecha_expiracion:
            self.fecha_expiracion = timezone.now().date() + datetime.timedelta(days=365*4)
        if not self.codigo_seguridad or Tarjeta.objects.filter(codigo_seguridad=self.codigo_seguridad).exists():
            self.codigo_seguridad = self.generar_codigo_seguridad()
        super().save(*args, **kwargs)

    def procesar_pago(self, monto, cooperativa=None):
        if not isinstance(monto, Decimal):
            raise ValueError("El monto debe ser un número decimal.")
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a cero.")
        if monto > self.saldo_asociado:
            raise ValueError("Saldo insuficiente para realizar el pago.")
        self.saldo_asociado -= monto
        self.save()

        pago = PagoPasaje.objects.create(
            id_tarjeta=self,
            monto=monto,
            id_cooperativa=cooperativa
        )
        return pago

    def procesar_recarga(self, monto):
        if not isinstance(monto, Decimal):
            raise ValueError("El monto debe ser un número decimal.")
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a cero.")
        self.saldo_asociado += monto
        self.save()

        recarga = RecargaSaldo.objects.create(
            id_tarjeta=self,
            monto=monto
        )
        return recarga

    def __str__(self):
        return self.numero_tarjeta


class RecargaSaldo(models.Model):
    id_recarga = models.AutoField(primary_key=True)
    id_tarjeta = models.ForeignKey('Tarjeta', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_y_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Recarga de {self.monto} para la tarjeta {self.id_tarjeta.numero_tarjeta}'


class PagoPasaje(models.Model):
    id_tarjeta = models.ForeignKey(Tarjeta, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    id_cooperativa = models.ForeignKey(CooperativaTransporte, on_delete=models.CASCADE)
    cantidad_pasajes = models.PositiveIntegerField(default=1)  # Este campo es necesario
    fecha_pago = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago {self.id} - {self.monto} USD ({self.cantidad_pasajes} pasajes)"

