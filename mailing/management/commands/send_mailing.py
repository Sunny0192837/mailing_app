from django.core.management import BaseCommand

from mailing.models import Mailing


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--mailing-id", type=int, help="ID рассылки")

    def handle(self, *args, **options):
        mailing_id = options.get("mailing_id")

        if mailing_id:
            try:
                mailing = Mailing.objects.get(id=mailing_id)
                mailing.status = Mailing.STATUS_STARTED
                mailing.save()
                mailing.send_mailing()
            except Mailing.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Рассылка с ID {mailing_id} не существует")
                )
        else:
            self.stdout.write(self.style.ERROR(f"Передайте --mailing-id"))
