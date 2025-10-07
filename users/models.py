from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    token = models.CharField(max_length=100, blank=True, null=True)
    username = None
    email = models.EmailField(
        unique=True, verbose_name="почта", help_text="Введите электронную почту"
    )
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="телефон",
        help_text="Введите номер телефона",
        blank=True,
        null=True,
    )
    country = models.CharField(
        max_length=255, verbose_name="страна", blank=True, null=True
    )
    image = models.ImageField(upload_to="users/avatars", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
