from django.contrib import admin
from .models import Bot, Scenario, Step, BotSettings, Conversation, Message


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ["name", "bot_type", "is_active", "owner", "created_at"]
    list_filter = ["bot_type", "is_active", "created_at"]
    search_fields = ["name", "description"]


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "owner", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ["name", "scenario", "step_type", "order"]
    list_filter = ["step_type", "scenario"]
    search_fields = ["name", "content"]


@admin.register(BotSettings)
class BotSettingsAdmin(admin.ModelAdmin):
    list_display = ["bot", "mistral_model", "max_tokens"]
    search_fields = ["bot__name"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["bot", "user_identifier", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["user_identifier", "bot__name"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["conversation", "timestamp", "has_user_message", "has_bot_message"]
    list_filter = ["timestamp"]

    def has_user_message(self, obj):
        return bool(obj.user_message)

    has_user_message.boolean = True

    def has_bot_message(self, obj):
        return bool(obj.bot_message)

    has_bot_message.boolean = True
