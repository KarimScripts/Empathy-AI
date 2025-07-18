import random
import os
import re
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

class ResponseGenerator:
    def __init__(self):
        """
        Initializes the ResponseGenerator with an API client and pre-defined responses.
        """
        try:
            self.api_client = InferenceClient(
                provider="nscale",
                api_key=os.getenv("HF_TOKEN"),
            )
        except Exception as e:
            print(f"Warning: Could not initialize API client: {e}")
            self.api_client = None

        self.responses = {
            "sadness": [
                "I'm so sorry to hear that you're feeling this way. Please know that your feelings are valid.",
                "It sounds like you're going through a lot right now. Remember that it's okay to not be okay.",
                "I hear you, and I want you to know that you're not alone in this. Sending you strength.",
                "That sounds incredibly tough. Please be gentle with yourself."
            ],
            "joy": [
                "That's wonderful to hear! I'm so happy for you.",
                "Wow, that's fantastic news! Thanks for sharing your joy with me.",
                "That sounds amazing! It's great to see you so happy.",
                "Your happiness is contagious! I'm smiling right along with you."
            ],
            "anger": [
                "It's completely understandable to feel angry in this situation. Your feelings are justified.",
                "That sounds incredibly frustrating. It's okay to feel angry about it.",
                "I can hear the anger in your words. It's important to let that emotion out.",
                "It takes a lot of energy to be that angry. Make sure you take some time for yourself."
            ],
            "fear": [
                "That sounds really scary. It's okay to feel afraid.",
                "I can only imagine how you must be feeling. Remember to breathe, you are safe here.",
                "It's brave of you to share your fears. Please know I'm here to listen without judgment.",
                "Feeling fearful is a natural response. You're not alone in this."
            ],
            "surprise": [
                "Wow, that's quite a surprise! Tell me more about it.",
                "Oh, I wasn't expecting that! That's really something.",
                "That's an interesting turn of events! How are you feeling about it?",
                "Well, that's a new development! Life is full of surprises."
            ],
            "disgust": [
                "That sounds like a really unpleasant experience. It's understandable to feel that way.",
                "I'm sorry you had to go through that. It's okay to feel disgusted by it.",
                "That's a strong and valid reaction to have. Your feelings make sense.",
                "It's okay to be repulsed by something like that. Thank you for sharing with me."
            ],
            "neutral": [
                "Thanks for sharing that with me. How are you feeling about it?",
                "I see. Is there anything else on your mind?",
                "Got it. I'm here to listen if you want to talk more.",
                "Thank you for telling me. I'm here for you."
            ],
            "default": [
                "Thank you for sharing that with me. It takes courage to be open.",
                "I'm here to listen whenever you need to talk.",
                "I appreciate you telling me this."
            ]
        }

    def generate_llm_response(self, emotion: str, user_message: str, recent_context=None, emotion_summary=None) -> str:
        """
        Generates a dynamic, empathetic response using an LLM, with context and emotion summary.
        """
        if not self.api_client:
            print("Warning: API client not available. Falling back to template response.")
            return self.generate_template_response(emotion)

        # Build context string from recent conversation
        context_str = ""
        if recent_context:
            for turn in recent_context:
                if turn["role"] == "user":
                    context_str += f"User: {turn['content']}\n"
                elif turn["role"] == "assistant":
                    context_str += f"AI: {turn['content']}\n"

        system_prompt = (
            f"You are an empathetic AI companion and the user's best friend. "
            f"Always respond with warmth, validation, and non-judgment. "
            f"After your main response, gently ask a follow-up question to encourage the user to share more or reflect. "
            f"Your goal is to make the user feel truly heard, supported, and never alone. "
            f"Be conversational, supportive, and inviting. "
            f"The user is feeling {emotion}. "
            f"{emotion_summary if emotion_summary else ''} "
            f"Here is the recent conversation:\n{context_str}"
            f"Respond in 2-4 sentences."
        )

        try:
            response = self.api_client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=180,
                temperature=0.7,
            )
            response_text = response.choices[0].message.content.strip()
            return response_text
        except Exception as e:
            print(f"Error during API call: {e}")
            return self.generate_template_response(emotion)

    def generate_template_response(self, emotion: str) -> str:
        """
        Generates an empathetic response based on the detected emotion using templates.

        Args:
            emotion: The emotion string (e.g., "sadness").

        Returns:
            A pre-written empathetic response string.
        """
        response_list = self.responses.get(emotion, self.responses["default"])
        return random.choice(response_list)

    def generate_response(self, emotion: str, user_message: str, recent_context=None, emotion_summary=None) -> str:
        """
        Generates an empathetic response, trying the LLM first and falling back to templates.

        Args:
            emotion: The emotion string (e.g., "sadness").
            user_message: The user's original message.

        Returns:
            An empathetic response string.
        """
        if self.api_client:
            return self.generate_llm_response(emotion, user_message, recent_context, emotion_summary)
        else:
            return self.generate_template_response(emotion)


if __name__ == '__main__':
    # Example usage
    generator = ResponseGenerator()
    
    emotions_and_messages = {
        "sadness": "I feel like nothing I do is good enough anymore.",
        "joy": "I am so happy and excited about the new project!",
        "love": "I am so in love with my new puppy."
    }
    
    print("--- Template Responses ---")
    for emotion, message in emotions_and_messages.items():
        response = generator.generate_template_response(emotion)
        print(f"Emotion: {emotion}")
        print(f"User Message: {message}")
        print(f"Response: {response}\n")

    if generator.api_client:
        print("\n--- LLM Responses ---")
        for emotion, message in emotions_and_messages.items():
            response = generator.generate_llm_response(emotion, message)
            print(f"Emotion: {emotion}")
            print(f"User Message: {message}")
            print(f"Response: {response}\n")
