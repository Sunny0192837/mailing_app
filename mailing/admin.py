from django.contrib import admin

from mailing.models import Client, Mailing, MailingAttempt, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name")
    list_filter = ("email",)
    search_fields = ("email", "comment")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subject",
    )
    list_filter = ("subject",)
    search_fields = ("subject", "body")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "message",
    )
    list_filter = ("clients",)
    search_fields = ("message", "clients")


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "mailing")
    list_filter = ("mailing",)
    search_fields = ("message", "clients")
