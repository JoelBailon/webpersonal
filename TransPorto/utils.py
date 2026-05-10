from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

def authenticate_by_email(request, email=None, password=None):
    UserModel = get_user_model()
    if email is None or password is None:
        return None
    
    try:
        # Busca el usuario por correo electrónico
        user = UserModel.objects.get(email=email)
    except UserModel.DoesNotExist:
        return None
    except ValidationError:
        # Maneja errores de validación si es necesario
        return None

    # Verifica la contraseña
    if user.check_password(password):
        return user
    
    return None
