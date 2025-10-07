from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        group = Group.objects.get_or_create(name="Managers")[0]

        manager_user = User.objects.get_or_create(email="manager_user@example.com")[0]
        manager_user.set_password("123qweasdzxc")
        manager_user.is_active = True
        manager_user.groups.add(group)
        manager_user.save()
