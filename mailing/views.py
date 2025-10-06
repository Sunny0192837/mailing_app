from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from users.models import User

from .forms import ClientForm, MailingForm, MessageForm
from .models import Client, Mailing, Message


class IndexView(TemplateView):
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "total_mailings": Mailing.objects.all().count(),
                "active_users": User.objects.all().count(),
                "unique_clients": Client.objects.all().count(),
            }
        )
        return context


class ClientListView(ListView):
    model = Client
    context_object_name = "clients"


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("mailing:client_list")


class ClientDeleteView(DeleteView):
    model = Client
    success_url = reverse_lazy("mailing:client_list")


# Сообщения (аналогично клиентам)
class MessageListView(ListView):
    model = Message
    context_object_name = "messages"


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(DeleteView):
    model = Message
    success_url = reverse_lazy("mailing:message_list")


# Рассылки
class MailingListView(ListView):
    model = Mailing
    context_object_name = "mailings"

    def get_queryset(self):
        return Mailing.objects.prefetch_related("clients", "message")


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDeleteView(DeleteView):
    model = Mailing
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDetailView(DetailView):
    model = Mailing

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attempts"] = self.object.attempts.all()
        return context


def start_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    if mailing.status == "created":
        mailing.status = "started"
        mailing.save()

    successful_sends = mailing.send_mailing()

    if successful_sends > 0:
        messages.success(
            request, f"Рассылка запущена! Успешно отправлено: {successful_sends}"
        )
    else:
        messages.error(request, "Ошибка при отправке рассылки")

    return redirect("mailing:mailing_detail", pk=pk)
