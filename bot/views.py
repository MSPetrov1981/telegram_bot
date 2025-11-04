from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Bot, Scenario, Step, BotSettings, Conversation
from .serializers import (
    BotSerializer,
    ScenarioSerializer,
    StepSerializer,
    BotSettingsSerializer,
    ConversationSerializer,
    StepCreateSerializer,
)
from .telegram_handler import TelegramBotHandler

# Webhook view for Telegram
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


@csrf_exempt
def telegram_webhook(request, bot_token):
    if request.method == "POST":
        try:
            # Find bot by token
            bot = Bot.objects.get(token=bot_token, is_active=True)

            # Process the update
            handler = TelegramBotHandler(bot)
            handler.handle_update(json.loads(request.body))

            return JsonResponse({"status": "ok"})
        except Bot.DoesNotExist:
            return JsonResponse({"error": "Bot not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


class BotViewSet(viewsets.ModelViewSet):
    serializer_class = BotSerializer

    def get_queryset(self):
        return Bot.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        bot = self.get_object()
        bot.is_active = True
        bot.save()
        return Response({"status": "bot activated"})

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        bot = self.get_object()
        bot.is_active = False
        bot.save()
        return Response({"status": "bot deactivated"})

    @action(detail=True, methods=["post"])
    def set_webhook(self, request, pk=None):
        bot = self.get_object()
        if bot.bot_type != "telegram":
            return Response(
                {"error": "Only telegram bots support webhooks"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        handler = TelegramBotHandler(bot)
        success = handler.set_webhook()

        if success:
            webhook_info = handler.get_webhook_info()
            return Response(
                {
                    "status": "webhook set successfully",
                    "webhook_info": {
                        "url": webhook_info.url if webhook_info else "Unknown",
                        "has_custom_certificate": webhook_info.has_custom_certificate
                        if webhook_info
                        else False,
                        "pending_update_count": webhook_info.pending_update_count
                        if webhook_info
                        else 0,
                    },
                }
            )
        else:
            return Response(
                {"error": "Failed to set webhook"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"])
    def delete_webhook(self, request, pk=None):
        bot = self.get_object()
        if bot.bot_type != "telegram":
            return Response(
                {"error": "Only telegram bots support webhooks"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        handler = TelegramBotHandler(bot)
        success = handler.delete_webhook()

        if success:
            return Response({"status": "webhook deleted successfully"})
        else:
            return Response(
                {"error": "Failed to delete webhook"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["get"])
    def webhook_info(self, request, pk=None):
        bot = self.get_object()
        if bot.bot_type != "telegram":
            return Response(
                {"error": "Only telegram bots support webhooks"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        handler = TelegramBotHandler(bot)
        webhook_info = handler.get_webhook_info()

        if webhook_info:
            return Response(
                {
                    "url": webhook_info.url,
                    "has_custom_certificate": webhook_info.has_custom_certificate,
                    "pending_update_count": webhook_info.pending_update_count,
                    "last_error_date": webhook_info.last_error_date,
                    "last_error_message": webhook_info.last_error_message,
                    "max_connections": webhook_info.max_connections,
                    "allowed_updates": webhook_info.allowed_updates,
                }
            )
        else:
            return Response(
                {"error": "Failed to get webhook info"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ScenarioViewSet(viewsets.ModelViewSet):
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        return Scenario.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"])
    def steps(self, request, pk=None):
        scenario = self.get_object()
        steps = scenario.steps.all()
        serializer = StepSerializer(steps, many=True)
        return Response(serializer.data)


class StepViewSet(viewsets.ModelViewSet):
    serializer_class = StepCreateSerializer

    def get_queryset(self):
        return Step.objects.filter(scenario__owner=self.request.user)

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return StepSerializer
        return StepCreateSerializer


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(bot__owner=self.request.user)


class BotSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = BotSettingsSerializer

    def get_queryset(self):
        return BotSettings.objects.filter(bot__owner=self.request.user)
