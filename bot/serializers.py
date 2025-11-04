from rest_framework import serializers
from .models import Bot, Scenario, Step, BotSettings, Conversation, Message


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = "__all__"


class ScenarioSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, read_only=True)

    class Meta:
        model = Scenario
        fields = "__all__"


class BotSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotSettings
        fields = "__all__"


class BotSerializer(serializers.ModelSerializer):
    settings = BotSettingsSerializer(read_only=True)
    scenario_details = ScenarioSerializer(source="scenario", read_only=True)

    class Meta:
        model = Bot
        fields = "__all__"
        read_only_fields = ("owner", "created_at", "updated_at")


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = "__all__"


class StepCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = "__all__"
