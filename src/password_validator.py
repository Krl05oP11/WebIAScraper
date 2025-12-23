"""
Password validation helper
Validates password strength requirements for WebIAScrap
"""
import re


def validate_password(password):
    """
    Valida que la contraseña cumpla con los requisitos de seguridad

    Requisitos:
    - Mínimo 8 caracteres
    - Al menos 1 letra mayúscula (A-Z)
    - Al menos 1 letra minúscula (a-z)
    - Al menos 1 número (0-9)
    - Al menos 1 símbolo especial

    Args:
        password (str): La contraseña a validar

    Returns:
        tuple: (is_valid: bool, error_message: str or None)

    Examples:
        >>> validate_password("Abc123!@")
        (True, None)

        >>> validate_password("weak")
        (False, "La contraseña debe tener al menos 8 caracteres")
    """
    if not password:
        return False, "La contraseña no puede estar vacía"

    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"

    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una letra mayúscula (A-Z)"

    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una letra minúscula (a-z)"

    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número (0-9)"

    # Símbolos especiales comunes
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        return False, "La contraseña debe contener al menos un símbolo especial (!@#$%^&*...)"

    return True, None


def get_password_requirements():
    """
    Retorna la lista de requisitos de contraseña para mostrar en UI

    Returns:
        list: Lista de strings con los requisitos de contraseña

    Example:
        >>> reqs = get_password_requirements()
        >>> print(reqs[0])
        'Mínimo 8 caracteres'
    """
    return [
        "Mínimo 8 caracteres",
        "Al menos una letra mayúscula (A-Z)",
        "Al menos una letra minúscula (a-z)",
        "Al menos un número (0-9)",
        "Al menos un símbolo especial (!@#$%^&*...)"
    ]
