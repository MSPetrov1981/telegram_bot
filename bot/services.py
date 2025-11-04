
# from mistralai import MistralClient
from .mistral_client import MistralAPIClient
from .models import Conversation, Message


class MistralService:
    def __init__(self, bot):
        self.bot = bot
        self.settings = bot.settings
        self.client = MistralAPIClient(api_key=self.settings.mistral_api_key)

    def generate_response(self, user_message, conversation_context=None):
        """Generate response using Mistral API"""
        try:
            messages = self._prepare_messages(user_message, conversation_context)

            response = self.client.chat_completion(
                model=self.settings.mistral_model,
                messages=messages,
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature,
            )

            return response
        except Exception as e:
            print(f"Mistral API error: {e}")
            return "I'm sorry, I'm having trouble processing your request right now."

    def _prepare_messages(self, user_message, conversation_context):
        """Prepare message history for context"""
        messages = []

        # Add system prompt if available
        if hasattr(self.bot, "scenario") and self.bot.scenario:
            system_prompt = self._get_system_prompt()
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

        # Add conversation history
        if conversation_context:
            # Get recent messages from conversation
            recent_messages = Message.objects.filter(
                conversation=conversation_context
            ).order_by("-timestamp")[:10]  # Last 10 messages

            for msg in reversed(recent_messages):  # Oldest first
                if msg.user_message:
                    messages.append({"role": "user", "content": msg.user_message})
                if msg.bot_message:
                    messages.append({"role": "assistant", "content": msg.bot_message})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def _get_system_prompt(self):
        """Generate system prompt from scenario steps"""
        if not self.bot.scenario:
            return "You are a helpful AI assistant."

        # Build prompt from scenario steps
        prompt_parts = [
            "You are an AI assistant following a specific conversation flow."
        ]

        steps = self.bot.scenario.steps.all().order_by("order")
        for step in steps:
            if step.step_type == "message":
                prompt_parts.append(f"When at step '{step.name}': {step.content}")
            elif step.step_type == "question":
                prompt_parts.append(f"When asking: {step.content}")

        return " ".join(prompt_parts)


class ScenarioProcessor:
    def __init__(self, bot, user_identifier):
        self.bot = bot
        self.user_identifier = user_identifier
        self.mistral_service = MistralService(bot)

    def process_message(self, user_message):
        """Process user message according to scenario"""
        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            bot=self.bot,
            user_identifier=self.user_identifier,
            defaults={"is_active": True},
        )

        # If new conversation, start from initial step
        if created and self.bot.scenario and self.bot.scenario.initial_step:
            conversation.current_step = self.bot.scenario.initial_step
            conversation.save()

        # Process based on current step
        if conversation.current_step:
            return self._process_with_scenario(conversation, user_message)
        else:
            return self._process_with_mistral(conversation, user_message)

    def _process_with_scenario(self, conversation, user_message):
        """Process message according to scenario steps"""
        current_step = conversation.current_step

        # Save user message
        Message.objects.create(
            conversation=conversation, step=current_step, user_message=user_message
        )

        # Handle different step types
        if current_step.step_type == "message":
            response = current_step.content
            next_step = current_step.next_step

        elif current_step.step_type == "question":
            # Use Mistral to generate response based on user's answer
            response = self.mistral_service.generate_response(
                user_message, conversation
            )
            next_step = current_step.next_step

        elif current_step.step_type == "api_call":
            # Handle API calls (simplified)
            response = f"API call would be made: {current_step.content}"
            next_step = current_step.next_step

        else:
            response = self.mistral_service.generate_response(
                user_message, conversation
            )
            next_step = None

        # Save bot response
        Message.objects.create(
            conversation=conversation, step=current_step, bot_message=response
        )

        # Update conversation state
        if next_step:
            conversation.current_step = next_step
        else:
            conversation.current_step = None
        conversation.save()

        return response

    def _process_with_mistral(self, conversation, user_message):
        """Fallback to direct Mistral processing"""
        response = self.mistral_service.generate_response(user_message, conversation)

        # Save messages
        Message.objects.create(conversation=conversation, user_message=user_message)
        Message.objects.create(conversation=conversation, bot_message=response)

        return response
