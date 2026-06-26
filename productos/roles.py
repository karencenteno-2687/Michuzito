from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


def get_user_role(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return "Admin"
    groups = user.groups.values_list("name", flat=True)
    for role in ["Admin", "Cocina", "Cajero"]:
        if role in groups:
            return role
    return None


def role_redirect(user):
    role = get_user_role(user)
    if role == "Cocina":
        return "cocina:dashboard"
    return "productos:list"


class RoleRequiredMixin(AccessMixin):
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        role = get_user_role(request.user)
        if role not in self.allowed_roles:
            if role == "Cocina":
                return redirect("cocina:dashboard")
            return redirect("productos:list")
        return super().dispatch(request, *args, **kwargs)
