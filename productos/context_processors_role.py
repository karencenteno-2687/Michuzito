from .roles import get_user_role


def role_context(request):
    if request.user.is_authenticated:
        return {
            "user_role": get_user_role(request.user),
            "is_admin": get_user_role(request.user) == "Admin",
            "is_cocina": get_user_role(request.user) == "Cocina",
            "is_cajero": get_user_role(request.user) == "Cajero",
        }
    return {
        "user_role": None,
        "is_admin": False,
        "is_cocina": False,
        "is_cajero": False,
    }
