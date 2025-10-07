from django.core.mail import send_mail
from django.db import models
from django.utils import timezone


class Client(models.Model):
    """
    Модель получателя рассылки.
    """

    email = models.EmailField(
        unique=True,
        verbose_name="почта получателя рассылки"
    )
    full_name = models.CharField(
        max_length=255,
        verbose_name="фио получателя рассылки"
    )
    comment = models.TextField(
        blank=True,
        verbose_name="комментарий",
        max_length=3000
    )
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="владелец"
    )

    def __str__(self):
        return f"{self.email} - {self.full_name}"

    class Meta:
        verbose_name = "получатель рассылки"
        verbose_name_plural = "получатели"


class Message(models.Model):
    """
    Модель сообщения
    """

    subject = models.CharField(
        max_length=255,
        verbose_name="тема сообщения"
    )
    body = models.TextField(
        max_length=4000,
        verbose_name="текст сообщения"
    )
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="владелец"
    )

    def __str__(self):
        return f"сообщение с темой: {self.subject}"

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"


class Mailing(models.Model):
    """
    Модель рассылки
    """

    STATUS_CREATED = "created"
    STATUS_STARTED = "started"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_STARTED, "Запущена"),
        (STATUS_COMPLETED, "Завершена"),
    ]

    start_time = models.DateTimeField(
        blank=True,
        null=True
    )
    end_time = models.DateTimeField(
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="created",
        verbose_name="статус рассылки",
    )
    message = models.ForeignKey(
        "mailing.Message",
        on_delete=models.CASCADE,
        verbose_name="сообщение"
    )
    clients = models.ManyToManyField(
        "mailing.Client",
        verbose_name="получатели рассылки"
    )
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="владелец"
    )

    def __str__(self):
        return f"Рассылка #{self.id} - {self.message.subject}"

    def send_mailing(self):
        """Отправка рассылки всем клиентам."""

        if self.status != self.STATUS_STARTED:
            return False

        self.start_time = timezone.now()
        self.save()

        successful_sends = 0
        for client in self.clients.all():
            attempt = MailingAttempt(mailing=self)
            try:
                send_mail(
                    subject=self.message.subject,
                    message=self.message.body,
                    from_email="yaprostodanil@yandex.ru",
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                attempt.recipient = client.email
                attempt.status = MailingAttempt.STATUS_SUCCESS
                attempt.server_response = "Успешно отправлено"
                successful_sends += 1
            except Exception as e:
                attempt.status = MailingAttempt.STATUS_FAILURE
                attempt.server_response = str(e)
            attempt.save()

        self.end_time = timezone.now()
        self.status = self.STATUS_COMPLETED
        self.save()

        return successful_sends

    class Meta:
        verbose_name = "рассылка"
        verbose_name_plural = "рассылки"


class MailingAttempt(models.Model):
    """
    Модель попытки рассылки
    """

    STATUS_SUCCESS = "success"
    STATUS_FAILURE = "failure"

    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Успешно"),
        (STATUS_FAILURE, "Не успешно"),
    ]

    recipient = models.CharField(max_length=255)
    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )
    server_response = models.TextField(blank=True)
    mailing = models.ForeignKey(
        "mailing.Mailing", on_delete=models.CASCADE, related_name="attempts"
    )

    def __str__(self):
        return f"Попытка {self.mailing} - {self.get_status_display()}"

    class Meta:
        verbose_name = "попытка рассылки"
        verbose_name_plural = "попытки рассылки"
