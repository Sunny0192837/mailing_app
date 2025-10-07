from django.urls import path

from mailing import views
from mailing.apps import MailingConfig
from mailing.views import MailingAttemptsView

app_name = MailingConfig.name

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path(
        "clients/",
         views.ClientListView.as_view(),
        name="client_list"
    ),
    path(
        "clients/create/",
         views.ClientCreateView.as_view(),
         name="client_create"
    ),
    path(
        "clients/<int:pk>/edit/",
        views.ClientUpdateView.as_view(),
        name="client_update"
    ),
    path(
        "clients/<int:pk>/delete/",
        views.ClientDeleteView.as_view(),
        name="client_delete",
    ),
    path(
        "messages/",
        views.MessageListView.as_view(),
        name="message_list"
    ),
    path(
        "messages/create/",
        views.MessageCreateView.as_view(),
        name="message_create"
    ),
    path(
        "messages/<int:pk>/edit/",
        views.MessageUpdateView.as_view(),
        name="message_update",
    ),
    path(
        "messages/<int:pk>/delete/",
        views.MessageDeleteView.as_view(),
        name="message_delete",
    ),
    path(
        "mailings/",
        views.MailingListView.as_view(),
        name="mailing_list"
    ),
    path(
        "mailings/create/",
        views.MailingCreateView.as_view(),
        name="mailing_create"
    ),
    path(
        "mailings/<int:pk>/",
        views.MailingDetailView.as_view(),
        name="mailing_detail"
    ),
    path(
        "mailings/<int:pk>/edit/",
        views.MailingUpdateView.as_view(),
        name="mailing_update",
    ),
    path(
        "mailings/<int:pk>/delete/",
        views.MailingDeleteView.as_view(),
        name="mailing_delete",
    ),
    path(
        "mailings/<int:pk>/start/",
         views.start_mailing,
         name="mailing_start"
    ),
    path(
        "attempts/",
         MailingAttemptsView.as_view(),
         name="mailing_attempts"
     ),
]
