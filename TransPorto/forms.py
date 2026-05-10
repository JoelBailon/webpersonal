from django import forms
from .models import Cliente, CooperativaTransporte

class ClienteCreationForm(forms.ModelForm):
    contraseña = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
        required=True
    )
    # Puedes eliminar esta parte si solo quieres tomar foto con la cámara y no subir archivo:
    foto_rostro = forms.ImageField(
        label='Foto de Rostro',
        required=False,  # Ahora no obligatorio porque la puedes tomar con la cámara
        widget=forms.ClearableFileInput(attrs={
            'class': 'block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer focus:outline-none'
        })
    )

    class Meta:
        model = Cliente
        fields = [
            'nombre', 'apellido', 'sexo', 'fecha_nacimiento',
            'direccion', 'numero_telefonico',
            'correo_electronico', 'nombre_usuario', 'foto_rostro'
        ]

    def save(self, commit=True):
        cliente = super().save(commit=False)
        cliente.set_password(self.cleaned_data['contraseña'])
        if commit:
            cliente.save()
        return cliente


class ClienteLoginForm(forms.Form):
    username_or_email = forms.CharField(
        label='Nombre de Usuario o Correo Electrónico',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 rounded-lg bg-white',
            'placeholder': 'Nombre de Usuario o Correo Electrónico',
            'required': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-3 rounded-lg bg-white',
            'placeholder': 'Contraseña',
            'required': True,
        })
    )


class RecargaSaldoForm(forms.Form):
    monto = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            'placeholder': 'Monto a recargar'
        })
    )


class PagoForm(forms.Form):
    cooperativa = forms.ModelChoiceField(
        queryset=CooperativaTransporte.objects.all(),
        empty_label="Selecciona una cooperativa",
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full p-2 border rounded'
        })
    )


class PagoQRForm(forms.Form):
    codigo_qr = forms.CharField(
        label='Código QR (Número de Tarjeta)',
        max_length=16,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border rounded',
            'placeholder': 'Escanea o ingresa el código QR'
        }),
        required=True
    )
