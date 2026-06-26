from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Producto, Categoria
from .validators import validate_image_file, validate_special_chars
import bleach


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre",
            "descripcion",
            "categoria",
            "precio",
            "imagen",
            "ingredientes",
            "tiempo_preparacion",
            "stock",
            "estado",
        ]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del producto",
                    "maxlength": 100,
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descripción del producto",
                    "rows": 3,
                }
            ),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "precio": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "imagen": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".jpg,.jpeg,.png,.webp",
                }
            ),
            "ingredientes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Carne, Lechuga, Tomate, Queso",
                }
            ),
            "tiempo_preparacion": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Tiempo en minutos",
                    "min": 1,
                }
            ),
            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0",
                    "min": 0,
                }
            ),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        validate_special_chars(nombre)
        return bleach.clean(nombre.strip())

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion")
        if descripcion:
            validate_special_chars(descripcion)
            return bleach.clean(descripcion.strip())
        return descripcion

    def clean_ingredientes(self):
        ingredientes = self.cleaned_data.get("ingredientes")
        if ingredientes:
            validate_special_chars(ingredientes)
            return bleach.clean(ingredientes.strip())
        return ingredientes

    def clean_imagen(self):
        imagen = self.cleaned_data.get("imagen")
        if imagen:
            validate_image_file(imagen)
        return imagen


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "estado"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre de la categoría",
                    "maxlength": 100,
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descripción de la categoría",
                    "rows": 2,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["estado"] = forms.ChoiceField(
            choices=[("True", "Activa"), ("False", "Inactiva")],
            widget=forms.Select(attrs={"class": "form-select"}),
            label="Estado",
            initial="True",
        )
        if self.instance and self.instance.pk is not None:
            self.fields["estado"].initial = str(self.instance.estado)

    def clean_estado(self):
        value = self.cleaned_data.get("estado")
        return value == "True"

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        validate_special_chars(nombre)
        return bleach.clean(nombre.strip())


class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "correo@ejemplo.com",
            }
        ),
    )
    first_name = forms.CharField(
        required=False,
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nombre",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Usuario"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Contraseña"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirmar contraseña"}
        )
