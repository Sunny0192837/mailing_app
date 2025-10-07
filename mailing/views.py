from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from users.models import User

from .forms import ClientForm, MailingForm, MessageForm
from .models import Client, Mailing, MailingAttempt, Message


class OwnerRequiredMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if (
            self.request.user.is_superuser
            or self.request.user.groups.filter(name="Managers").exists()
        ):
            return qs
        return qs.filter(owner=self.request.user)


class ManagerReadOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return not self.request.user.groups.filter(name="Managers").exists()

    def handle_no_permission(self):
        if self.request.user.groups.filter(name="Managers").exists():
            raise PermissionDenied(
                "Менеджеры могут только просматривать данные"
            )
        return super().handle_no_permission()


class ManagerAccessMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return not user.groups.filter(name="Managers").exists()

    def handle_no_permission(self):
        raise PermissionDenied("Менеджеры могут только просматривать данные")


class IndexView(TemplateView):
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        cache_key = "index_context_stats"
        cached_stats = cache.get(cache_key)

        if not cached_stats:
            cached_stats = {
                "total_mailings": Mailing.objects.count(),
                "active_users": User.objects.filter(is_active=True).count(),
                "unique_clients": Client.objects.distinct().count(),
            }
            cache.set(cache_key, cached_stats, 60)

        context = super().get_context_data(**kwargs)
        context.update(cached_stats)
        return context


class MailingAttemptsView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailing/mailing_attempts.html"
    context_object_name = "attempts"
    paginate_by = 20

    def get_queryset(self):
        return (
            MailingAttempt.objects.filter(mailing__owner=self.request.user)
            .select_related("mailing")
            .order_by("-attempt_time")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_attempts = MailingAttempt.objects.filter(
            mailing__owner=self.request.user
        )

        context.update(
            {
                "total_attempts": user_attempts.count(),
                "successful_attempts": user_attempts.filter(
                    status=MailingAttempt.STATUS_SUCCESS
                ).count(),
                "failed_attempts": user_attempts.filter(
                    status=MailingAttempt.STATUS_FAILURE
                ).count(),
            }
        )
        return context


class ClientListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Client
    context_object_name = "clients"


class ClientCreateView(LoginRequiredMixin, ManagerAccessMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(
    LoginRequiredMixin, ManagerAccessMixin, OwnerRequiredMixin, UpdateView
):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("mailing:client_list")


class ClientDeleteView(
    LoginRequiredMixin, ManagerAccessMixin, OwnerRequiredMixin, DeleteView
):
    model = Client
    success_url = reverse_lazy("mailing:client_list")


class MessageListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Message
    context_object_name = "messages"


class MessageCreateView(LoginRequiredMixin, ManagerAccessMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(
    LoginRequiredMixin, ManagerAccessMixin, OwnerRequiredMixin, UpdateView
):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(
    LoginRequiredMixin, ManagerAccessMixin, OwnerRequiredMixin, DeleteView
):
    model = Message
    success_url = reverse_lazy("mailing:message_list")


class MailingListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Mailing
    context_object_name = "mailings"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related("clients", "message")


class MailingCreateView(LoginRequiredMixin, ManagerAccessMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(
    LoginRequiredMixin, ManagerAccessMixin, OwnerRequiredMixin, UpdateView
):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDeleteView(
    LoginRequiredMixin, ManagerAccessMixin, OwnerRequiredMixin, DeleteView
):
    model = Mailing
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Mailing

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attempts"] = self.object.attempts.all()
        return context


@login_required
def start_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    if request.user.groups.filter(name="Managers").exists():
        raise PermissionDenied("Менеджеры не могут запускать рассылки")

    if not request.user.is_superuser and mailing.owner != request.user:
        raise PermissionDenied("У вас нет прав для запуска этой рассылки")

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
