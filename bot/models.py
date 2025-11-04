from django.db import models
from django.contrib.auth.models import User


class Bot(models.Model):
    BOT_TYPES = [
        ("telegram", "Telegram Bot"),
        ("web", "Web Chat Bot"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    bot_type = models.CharField(max_length=20, choices=BOT_TYPES, default="telegram")
    token = models.CharField(max_length=200, blank=True)  # Telegram bot token
    webhook_url = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    scenario = models.ForeignKey(
        "Scenario", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bots"

    def __str__(self):
        return self.name


class Scenario(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    initial_step = models.ForeignKey(
        "Step",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="initial_scenarios",
    )
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "scenarios"

    def __str__(self):
        return self.name


class Step(models.Model):
    STEP_TYPES = [
        ("message", "Send Message"),
        ("question", "Ask Question"),
        ("condition", "Condition"),
        ("api_call", "API Call"),
    ]

    scenario = models.ForeignKey(
        Scenario, on_delete=models.CASCADE, related_name="steps"
    )
    name = models.CharField(max_length=100)
    step_type = models.CharField(max_length=20, choices=STEP_TYPES)
    content = models.TextField(help_text="Message text, question, or condition logic")
    order = models.IntegerField(default=0)
    next_step = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="previous_steps",
    )
    # For additional configuration
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "steps"
        ordering = ["scenario", "order"]

    def __str__(self):
        return f"{self.scenario.name} - {self.name}"


class BotSettings(models.Model):
    bot = models.OneToOneField(Bot, on_delete=models.CASCADE, related_name="settings")
    mistral_api_key = models.CharField(max_length=200)
    mistral_model = models.CharField(max_length=50, default="mistral-small-latest")
    max_tokens = models.IntegerField(default=500)
    temperature = models.FloatField(default=0.7)
    max_requests_per_minute = models.IntegerField(default=60)

    class Meta:
        db_table = "bot_settings"

    def __str__(self):
        return f"Settings for {self.bot.name}"


class Conversation(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    # Telegram chat_id or web user session
    user_identifier = models.CharField(max_length=100)
    current_step = models.ForeignKey(
        Step, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    context_data = models.JSONField(
        default=dict, blank=True
    )  # Store conversation context
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conversations"
        unique_together = ["bot", "user_identifier"]

    def __str__(self):
        return f"Conversation with {self.user_identifier} on {self.bot.name}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    step = models.ForeignKey(Step, on_delete=models.SET_NULL, null=True, blank=True)
    user_message = models.TextField(blank=True)
    bot_message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messages"
        ordering = ["timestamp"]

    def __str__(self):
        return f"Message at {self.timestamp}"
