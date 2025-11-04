from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"bots", views.BotViewSet, basename="bot")
router.register(r"scenarios", views.ScenarioViewSet, basename="scenario")
router.register(r"steps", views.StepViewSet, basename="step")
router.register(r"conversations", views.ConversationViewSet, basename="conversation")
router.register(r"settings", views.BotSettingsViewSet, basename="botsettings")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "webhook/telegram/<str:bot_token>/",
        views.telegram_webhook,
        name="telegram_webhook",
    ),
]
