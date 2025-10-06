from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from users.models import User


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ваш email",
                "autocomplete": "email",
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ваш пароль",
                "autocomplete": "current-password",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Электронная почта"


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Обновление атрибутов для email
        email_field = self.fields.get("email")
        email_field.widget.attrs.update(
            {"placeholder": "Адрес электронной почты", "class": "form-control"}
        )

        # Обновление атрибутов для паролей
        password1_field = self.fields.get("password1")
        password1_field.widget.attrs.update(
            {"placeholder": "Введите сложный пароль", "class": "form-control"}
        )

        password2_field = self.fields.get("password2")
        password2_field.widget.attrs.update(
            {"placeholder": "Введите пароль еще раз", "class": "form-control"}
        )

        # Удаление help_text
        for field in self.fields.values():
            field.help_text = None
