from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        user = User.objects.get_or_create(email="aboba228@aboba.com")[0]
        user.set_password("123qweasdzxc")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        user1 = User.objects.get_or_create(email="aboba229@aboba.com")[0]
        user1.set_password("1234qweasdzxc")
        user1.is_active = True
        user1.save()
