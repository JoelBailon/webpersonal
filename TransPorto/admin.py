from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from .models import Cliente, CooperativaTransporte, Rutas, UnidadTransporte, Conductores, Tarjeta
from django.utils.translation import gettext_lazy as _


class ClienteCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Cliente
        fields = ('nombre_usuario', 'correo_electronico')

    def clean_password2(self):
        pw1 = self.cleaned_data.get('password1')
        pw2 = self.cleaned_data.get('password2')
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError('Las contraseñas no coinciden')
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = self.cleaned_data['password1']  # Guardamos texto plano
        if commit:
            user.save()
        return user

class ClienteChangeForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

class ClienteAdmin(UserAdmin):
    add_form = ClienteCreationForm
    form = ClienteChangeForm
    model = Cliente

    list_display = ('nombre_usuario', 'correo_electronico', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')

    search_fields = ('nombre_usuario', 'correo_electronico')
    ordering = ('nombre_usuario',)

    fieldsets = (
        (None, {'fields': ('nombre_usuario', 'correo_electronico', 'password')}),
        (_('Información personal'), {'fields': ('nombre', 'apellido', 'sexo', 'fecha_nacimiento', 'numero_telefonico', 'direccion')}),
        (_('Permisos'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Fechas importantes'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nombre_usuario', 'correo_electronico', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

admin.site.register(Cliente, ClienteAdmin)
admin.site.register(CooperativaTransporte)
admin.site.register(Rutas)
admin.site.register(UnidadTransporte)
admin.site.register(Conductores)
admin.site.register(Tarjeta)
